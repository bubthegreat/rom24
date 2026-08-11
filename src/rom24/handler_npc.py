import copy
import os
import hashlib
import time
import logging
import json

logger = logging.getLogger(__name__)

from rom24 import living
from rom24 import bit
from rom24 import tables
from rom24 import handler_item
from rom24 import settings
from rom24 import instance
from rom24 import interp
from rom24 import game_utils
from rom24 import merc
from rom24 import state_checks


class Npc(living.Living):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        super().__init__()
        # self.is_npc = True
        self.vnum = 0  # Needs to come before the template to setup the instance
        self.memory = None
        self.spec_fun = None
        self.new_format = True
        self.area = ""
        self.off_flags = bit.Bit(flags=tables.off_flags)
        self.damage = [0, 0, 0]
        self.start_pos = 0
        self.default_pos = 0
        self.hit_dice = [0, 0, 0]
        self.mana_dice = [0, 0, 0]
        self.dam_dice = [0, 0, 0]
        self.template_wealth = 0
        self.count = 0
        self.killed = 0
        self.pShop = None
        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]
        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]
            self.instancer()
        if self.environment:
            if self._environment not in instance.global_instances.keys():
                self.environment = None
        if self.inventory:
            for instance_id in self.inventory[:]:
                handler_item.Items.load(instance_id=instance_id)
        for item_id in self.equipped.values():
            if item_id:
                handler_item.Items.load(instance_id=item_id)
        if self.instance_id:
            self.instance_setup()
            Npc.instance_count += 1
        else:
            Npc.template_count += 1
        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            logger.trace("Freeing %s" % str(self))
            if self.instance_id:
                Npc.instance_count -= 1
                if instance.characters.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Npc.template_count -= 1
        except:
            return

    def __repr__(self):
        if self.instance_id:
            return "<NPC Instance: %s ID %d template %d>" % (
                self.short_descr,
                self.instance_id,
                self.vnum,
            )
        else:
            return "<NPC Template: %s:%s>" % (self.short_descr, self.vnum)

    def instance_setup(self):
        instance.global_instances[self.instance_id] = self
        instance.npcs[self.instance_id] = self
        instance.characters[self.instance_id] = self
        if self.vnum not in instance.instances_by_npc.keys():
            instance.instances_by_npc[self.vnum] = [self.instance_id]
        else:
            instance.instances_by_npc[self.vnum] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_npc[self.vnum].remove(self.instance_id)
        del instance.npcs[self.instance_id]
        del instance.characters[self.instance_id]
        del instance.global_instances[self.instance_id]

    def interpret(self, argument):
        logger.debug("Npc %s ran %s", self.name, argument)

        # Strip leading spaces.
        argument = argument.lstrip()

        # No hiding.
        self.affected_by.rem_bit(merc.AFF_HIDE)

        if not argument:
            return

        # Grab the command word.
        # Special parsing so ' can be a command,
        #   also no spaces needed after punctuation.
        if not argument[0].isalpha() and not argument[0].isdigit():
            command = argument[0]
            argument = argument[:1].lstrip()
        else:
            argument, command = game_utils.read_word(argument)

        # Look for command in command table.
        trust = self.trust
        cmd = state_checks.prefix_lookup(interp.cmd_table, command)
        if cmd is not None:
            if cmd.level > trust:
                cmd = None

        if not cmd:
            # NPCs do not use the socials table (Pc.check_social is PC-only).
            self.send("Huh?\n")
            return

        # * Not in position for command?
        if self.position < cmd.position:
            if self.position == merc.POS_DEAD:
                self.send("Lie still; you are DEAD.\n")
            elif self.position == merc.POS_MORTAL or self.position == merc.POS_INCAP:
                self.send("You are hurt far too bad for that.\n")
            elif self.position == merc.POS_STUNNED:
                self.send("You are too stunned to do that.\n")
            elif self.position == merc.POS_SLEEPING:
                self.send("In your dreams, or what?\n")
            elif self.position == merc.POS_RESTING:
                self.send("Nah... You feel too relaxed...\n")
            elif self.position == merc.POS_SITTING:
                self.send("Better stand up first.\n")
            elif self.position == merc.POS_FIGHTING:
                self.send("No way!  You are still fighting!\n")
            return

        # Dispatch the command.
        if cmd.default_arg:
            cmd.do_fun(self, cmd.default_arg)
            return
        cmd.do_fun(self, argument.lstrip())

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ("desc", "send"):
                continue
            elif str(k) in ("_last_saved", "_md5"):
                continue
            else:
                tmp_dict[k] = v

        cls_name = "__class__/" + __name__ + "." + self.__class__.__name__
        return {cls_name: outer_encoder(tmp_dict)}

    @classmethod
    def from_json(cls, data, outer_decoder=None):
        if outer_decoder is None:
            outer_decoder = json.JSONDecoder.decode

        cls_name = "__class__/" + __name__ + "." + cls.__name__
        if cls_name in data:
            tmp_data = outer_decoder(data[cls_name])
            return cls(**tmp_data)
        return data

    def save(self, force: bool = False):
        if self._last_saved is None:
            self._last_saved = time.time() - settings.SAVE_LIMITER - 2
        if not force and time.time() < self._last_saved + settings.SAVE_LIMITER:
            return

        if self.instance_id:
            top_dir = settings.INSTANCE_DIR
            number = self.instance_id
        else:
            top_dir = settings.AREA_DIR
            number = self.vnum
        if self.in_area.instance_id:
            area_number = self.in_area.instance_id
        else:
            area_number = self.in_area.index
        pathname = os.path.join(
            top_dir, "%d-%s" % (area_number, self.in_area.name), "npcs"
        )

        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, "%d-npc.json" % number)
        # logger.info('Saving %s', filename)
        js = json.dumps(self, default=instance.to_json, indent=4, sort_keys=True)
        md5 = hashlib.md5(js.encode("utf-8")).hexdigest()
        if self._md5 != md5:
            self._md5 = md5
            with open(filename, "w") as fp:
                fp.write(js)

        if self.inventory:
            for item_id in self.inventory[:]:
                if item_id not in instance.items:
                    # logger.error('Item %d is in NPC %d\'s inventory, but does not exist?', item_id, self.instance_id)
                    continue
                item = instance.items[item_id]
                item.save(in_inventory=True, force=force)
        for item_id in self.equipped.values():
            if item_id:
                if item_id not in instance.items:
                    # logger.error('Item %d is in NPC %d\'s equipment, but does not exist?', item_id, self.instance_id)
                    continue
                item = instance.items[item_id]
                item.save(is_equipped=True, force=force)

    @classmethod
    def load(cls, vnum: int = None, instance_id: int = None):
        if instance_id:
            if instance_id in instance.characters:
                logger.warn("Instance %d of npc already loaded!", instance_id)
                return
            pathname = settings.INSTANCE_DIR
            number = instance_id
        elif vnum:
            pathname = settings.AREA_DIR
            number = vnum
        else:
            raise ValueError(
                "To load an NPC, you must provide either a VNUM or an Instance_ID!"
            )

        target_file = "%d-npc.json" % number
        filename = None
        for a_path, a_directory, i_files in os.walk(pathname):
            if target_file in i_files:
                filename = os.path.join(a_path, target_file)
                break
        if not filename:
            raise ValueError("Cannot find %s" % target_file)

        with open(filename, "r") as fp:
            obj = json.load(fp, object_hook=instance.from_json)
        if isinstance(obj, Npc):
            # This just ensures that all items the player has are actually loaded.
            if obj.inventory:
                for item_id in obj.inventory[:]:
                    handler_item.Items.load(instance_id=item_id)
            return obj
        else:
            logger.error("Could not load npc data for %d", number)
            return None
