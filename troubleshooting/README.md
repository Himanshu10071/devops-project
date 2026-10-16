# Troubleshooting lab

Three deliberately broken manifests for the "failure simulation" part of the demo. Apply one, diagnose it with the commands below, fix it, and clean up.

The lab Deployments carry a full securityContext so they pass the namespace's *restricted* Pod Security level. Otherwise admission would reject the pod before the lab's real failure could happen.

| Lab | File | Symptom | Root cause |
|-----|------|---------|------------|
| 1 | `broken-image.yaml` | `ImagePullBackOff` | Image tag does not exist in GHCR |
| 2 | `broken-service.yaml` | Service has no endpoints | Selector labels don't match any Pod; wrong `targetPort` |
| 3 | `broken-db-config.yaml` | `CrashLoopBackOff` | `DATABASE_URL` points at a host that doesn't exist |

## Diagnosis toolkit

```bash
kubectl get pods -n ironpulse                       # STATUS and RESTARTS
kubectl describe pod <pod> -n ironpulse             # Events at the bottom explain pull/schedule errors
kubectl logs <pod> -n ironpulse --previous          # logs of the crashed container
kubectl get events -n ironpulse --sort-by=.lastTimestamp
kubectl get svc,endpoints -n ironpulse              # a Service without endpoints selects nothing
kubectl get pods -n ironpulse --show-labels         # compare labels with the Service selector
```

## Lab 1 — ImagePullBackOff

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl describe pod -n ironpulse -l app=broken-image | tail -n 15
```

`describe` shows `Failed to pull image ... not found`. Fix it by setting the image to a tag CI actually pushed (the commit SHA shown in the GHCR package page) and re-applying.

## Lab 2 — Service without endpoints

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpoints -n ironpulse ironpulse-broken-service     # <none>
kubectl get pods -n ironpulse -l app.kubernetes.io/name=backend --show-labels
```

The selector says `app: ironpulse-api`, but the pods are labelled `app.kubernetes.io/name: backend`. A Service routes only to Pods whose labels match its selector: no match means no endpoints and no traffic. Fix the selector and set `targetPort: 8000`:

```bash
kubectl patch svc ironpulse-broken-service -n ironpulse --type merge -p \
  '{"spec":{"selector":{"app":null,"app.kubernetes.io/name":"backend","app.kubernetes.io/instance":"ironpulse"},"ports":[{"port":8000,"targetPort":8000}]}}'
kubectl get endpointslices -n ironpulse -l kubernetes.io/service-name=ironpulse-broken-service   # now lists the backend pod IPs
```

Note the `"app": null`. A merge patch *adds* keys to the selector, so without it the wrong `app` label stays in the selector and still matches nothing.

## Lab 3 — CrashLoopBackOff

```bash
kubectl apply -f troubleshooting/broken-db-config.yaml
kubectl logs -n ironpulse -l app=broken-db --previous
```

The logs show Alembic failing to resolve `postgres-does-not-exist`. The real chart reads `DATABASE_URL` from the `ironpulse-db` Secret, and the `/ready` probe would keep a misconfigured pod out of the load balancer.

## Clean up

```bash
kubectl delete -f troubleshooting/ --ignore-not-found
```
