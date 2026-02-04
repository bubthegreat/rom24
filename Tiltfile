# Tiltfile for pyrom local development
allow_k8s_contexts('docker-desktop')

# Build pyrom Docker image with live updates
docker_build('bubthegreat/pyrom',
    context='./',
    dockerfile='Dockerfile',
    live_update=[
        sync('./src/', '/pyrom/src/'),
        # Restart the server when Python files change
        run('pkill -f rom24 || true', trigger=['./src/rom24/']),
    ],
    ignore=[
        './.git/',
        './k8s/',
        './argocd/',
    ]
)

# Load the Kubernetes manifests using kustomize local overlay
k8s_yaml(kustomize('k8s/overlays/local'))

# Port forward the pyrom deployment
k8s_resource(workload='pyrom-deployment', port_forwards=1337)

