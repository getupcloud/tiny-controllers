# Tiny Controllers for Kubernetes

Tiny kubernetes controllers for tiny common tasks.

## List of available controllers

### Node Reconciler

Apply labels, annotations and taints from:

- node annotations started with `label.getup.io/$name` and `taint.getup.io.$name.[$value,$operator]`
- node labels started with `annotation.getup.io/$name` and `taint.getup.io.$name.[$value,$operator]`

Examples:

```
# Set node annotation `my-annotation: value` from label:
$ kubectl label node node1 annotation.getup.io.my-annotation=value

# Set node label my-label=123 from annotation:
$ kubectl annotate node node1 label.getup.io.my-label=123

# Set node taint dedicated=gpu:NoSchedule from label:
$ kubectl label node node1 taint.getup.io.dedicated.gpu=NoSchedule
```

### Job Cleanup

Removes old Job objects. This is intended for old Kubernetes versions which lacks builting Job cleanup.


## Installing

Preferred method to install is using helm:

```
$ git clone https://github.com/getupcloud/tiny-controllers.git
$ helm install tiny-controllers ./tiny-controllers/chart
```

## Building

Create a local image with:

```
# build local image
$ make image

# send it to dockerhub
$ make push

# build and run local dev image
$ make dev

# build, tag and relase
$ make release
```

Use make vars to overwrite defaults:

```
$ make release VERSION=v0.0.1 REPOSITORY=getupcloud IMAGE_NAME=tiny-controllers
```

Look into Makefile for more targets.
