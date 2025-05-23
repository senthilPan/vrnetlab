vrnetlab - VR Network Lab
-------------------------
Run your favourite virtual routers in docker for convenient labbing,
development and testing.

vrnetlab is being developed for the TeraStream project at Deutsche Telekom as
part of an automated CI environment for testing our network provisioning
system.

It supports:

 * Arista vEOS
 * Cisco CSR1000v
 * Cisco Nexus NX-OS (using Titanium emulator)
 * Cisco XRv
 * Cisco XRv 9000
 * Juniper vMX
 * Juniper vQFX
 * Nokia VSR
 
I talk a little about it during my presentation about TeraStream testing at
the NetNod autumn meeting 2016 - https://youtu.be/R_vCdGkGeSk?t=9m25s

Brian Linkletter has written a good introduction too https://www.brianlinkletter.com/vrnetlab-emulate-networks-using-kvm-and-docker/


Usage
-----
You have to build the virtual router docker images yourself since the license
agreements of commercial virtual routers do not allow me to distribute the
images. See the README files of the respective virtual router types for more
details.

You need KVM enabled in your kernel for hardware assisted virtualization. While
it may be possible to run without it, it has not been tested. Make sure you
load the kvm kernel module: `modprobe kvm`.

Let's assume you've built the `xrv` router.

Start two virtual routers:
```
docker run -d --name vr1 --privileged vr-xrv:5.3.3.51U
docker run -d --name vr2 --privileged vr-xrv:5.3.3.51U
```
I'm calling them vr1 and vr2. Note that I'm using XRv 5.3.3.51U - you should
fill in your XRv version in the image tag as the "latest" tag is not added to
any images.

It takes a few minutes for XRv to start but once up you should be able to SSH
into each virtual router. You can get the IP address using docker inspect:
```
root@host# docker inspect --format '{{.NetworkSettings.IPAddress}}' vr1
172.17.0.98
```
Now SSH to that address and login with the default credentials of
vrnetlab/VR-netlab9:
```
root@host# ssh -l vrnetlab $(docker inspect --format '{{.NetworkSettings.IPAddress}}' vr1)
The authenticity of host '172.17.0.98 (172.17.0.98)' can't be established.
RSA key fingerprint is e0:61:28:ba:12:77:59:5e:96:cc:58:e2:36:55:00:fa.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '172.17.0.98' (RSA) to the list of known hosts.

IMPORTANT:  READ CAREFULLY
Welcome to the Demo Version of Cisco IOS XRv (the "Software").
The Software is subject to and governed by the terms and conditions
of the End User License Agreement and the Supplemental End User
License Agreement accompanying the product, made available at the
time of your order, or posted on the Cisco website at
www.cisco.com/go/terms (collectively, the "Agreement").
As set forth more fully in the Agreement, use of the Software is
strictly limited to internal use in a non-production environment
solely for demonstration and evaluation purposes.  Downloading,
installing, or using the Software constitutes acceptance of the
Agreement, and you are binding yourself and the business entity
that you represent to the Agreement.  If you do not agree to all
of the terms of the Agreement, then Cisco is unwilling to license
the Software to you and (a) you may not download, install or use the
Software, and (b) you may return the Software as more fully set forth
in the Agreement.


Please login with any configured user/password, or cisco/cisco


vrnetlab@172.17.0.98's password:


RP/0/0/CPU0:ios#show version
Mon Jul 18 09:04:45.261 UTC

Cisco IOS XR Software, Version 5.3.3.51U[Default]
...
```

You can also login via NETCONF:
```
root@host# ssh -l vrnetlab $(docker inspect --format '{{.NetworkSettings.IPAddress}}' vr1) -p 830 -s netconf
vrnetlab@172.17.0.98's password:
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <capabilities>
  <capability>urn:ietf:params:netconf:base:1.1</capability>
  <capability>urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring</capability>
  <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:validate:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.1</capability>
  <capability>http://cisco.com/ns/yang/Cisco-IOS-XR-aaa-lib-cfg?module=Cisco-IOS-XR-aaa-lib-cfg&amp;revision=2015-08-27</capability>
  <capability>http://cisco.com/ns/yang/Cisco-IOS-XR-aaa-locald-admin-cfg?module=Cisco-IOS-XR-aaa-locald-admin-cfg&amp;revision=2015-08-27</capability>
  <capability>http://cisco.com/ns/yang/Cisco-IOS-XR-aaa-locald-cfg?module=Cisco-IOS-XR-aaa-locald-cfg&amp;revision=2015-08-27</capability>
  <capability>http://cisco.com/ns/yang/Cisco-IOS-XR-aaa-locald-oper?module=Cisco-IOS-XR-aaa-locald-oper&amp;revision=2015-08-27</capability>
  <capability>http://cisco.com/ns/yang/Cisco-IOS-XR-bundlemgr-cfg?module=Cisco-IOS-XR-bundlemgr-cfg&amp;revision=2015-08-27</capability>
...
```

The serial console of the devices are mapped to port 5000. Use telnet to connect:
```
root@host# telnet $(docker inspect --format '{{.NetworkSettings.IPAddress}}' vr1) 5000
```
Just like with any serial port, you can only have one connection at a time and
while the router is booting the launch script will connect to the serial port
to do the initialization of the router. As soon as it is done the port will be
released and made available to the next connection.

To connect two virtual routers with each other we can use the `vr-xcon`
container. Let's say we want to connect Gi0/0/0/0 of vr1 and vr2 with each
other, we would do:
```
docker run -d --name vr-xcon --link vr1 --link vr2 vr-xcon --p2p vr1/1--vr2/1
```

Configure a link network on vr1 and vr2 and you should be able to ping!
```
P/0/0/CPU0:ios(config)#inte GigabitEthernet 0/0/0/0
RP/0/0/CPU0:ios(config-if)#no shutdown
RP/0/0/CPU0:ios(config-if)#ipv4 address 192.168.1.2/24
RP/0/0/CPU0:ios(config-if)#commit
Mon Jul 18 09:13:24.196 UTC
RP/0/0/CPU0:Jul 18 09:13:24.216 : ifmgr[227]: %PKT_INFRA-LINK-3-UPDOWN : Interface GigabitEthernet0/0/0/0, changed state to Down
RP/0/0/CPU0:ios(config-if)#dRP/0/0/CPU0:Jul 18 09:13:24.256 : ifmgr[227]: %PKT_INFRA-LINK-3-UPDOWN : Interface GigabitEthernet0/0/0/0, changed state to Up
o ping 192.168.1.1
Mon Jul 18 09:13:26.896 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.1.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms
```
(obviously I configured the other end too!)

All of the NICs of the virtual routers are exposed via TCP ports by KVM. TCP
port 10001 maps to the first NIC of the virtual router, which in the case of an
XR router is GigabitEthernet 0/0/0/0. By simply connecting two of these TCP
sockets together we can bridge the traffic between those two NICs and this is
exactly what vr-xcon is for. Use the `--p2p` argument to specify the links.
The format is X/Y--Z/N where X is the name of the first router and Y is the
port on that router. Z is the second router and N is the port on the second
router.

To set up more than one p2p link, simply add more mappings separated by space
and don't forget to link the virtual routers:
```
docker run -d --name vr-xcon --link vr1 --link vr2 --link vr3 vr-xcon --p2p vr1/1--vr2/1 vr1/2--vr3/1
```
See topology-machine/README.md for details on topology machine which can help
you with managing more complex topologies.

The containers expose port 22 for SSH, port 161 for SNMP, port 830 for NETCONF
and port 5000 is mapped to the virtual serial device (use telnet). All the NICs
of the virtual routers are exposed via TCP ports in the range 10001-10099.

Use `docker rm -f vr1` to stop and remote a virtual router.

Handy shell functions
---------------------
There are some handy shell functions in vrnetlab.sh that provides shorthands
for connecting to ssh and console.

1. Load the functions into your shell
```
. vrnetlab.sh
```
2. Login via ssh to router vr1, you can optionally specify a username. If no
username is provided, the default of vrnetlab will be used. If sshpass is
installed, you will not be promted for password when you login with the default
username.
```
vrssh vr1 myuser 
```
3. Connect console to router vr1
```
vrcons vr1
```
4. Create a bridge between two router interfaces, the below command bridges
interface 1 of router vr1 with interface 1 of router 2.
```
vrbridge vr1 1 vr2 1
```

To load these aliases on login, copy it to ~/.vrnetlab_bashrc and add the
following to your .bashrc
```
test -f ~/.vrnetlab_bashrc && . ~/.vrnetlab_bashrc
``` 


Virtual routers
---------------
There are a number of virtual routers available on the market:

 * Cisco XRv
 * Juniper VRR
 * Juniper vMX
 * Nokia VSR

All of the above are released as a qcow2 or vmdk file (which can easily be
converted into qcow2) making them easy to spin up on a Linux machine. Once spun
up there are a few tasks one normally wants to perform:

 * set an IP address on a management interface
 * start SSH / NETCONF daemon (and generate crypto keys)
 * create initial user so we can login

There might be more things to the list but this is the bare minimum which makes
the router remotely reachable and thus we can configure the rest from the
normal provisioning system.

vrnetlab aims to make this process as simple and convenient as possible so that
it may be used both by humans and automated systems to spin up virtual routers.
In addition, there are scripts to help you generate topologies.

The virtual machines are packaged up in docker container. Since we need to
start KVM the docker containers have to be run with `--privileged` which
effectively defeats the security features of docker. Our use of docker is
essentially reduced to being a packaging format but a rather good one at that.
Also note that since we still rely on KVM the same amount of resources, if not
sightly more, will be consumed by vrnetlab. A container is no thinner than a VM
if the container contains a VM!

The assignment of a management IP address is handed over to docker, so you can
use whatever docker IPAM plugin you want. Overall the network setup of the
virtual routers are kind of shoe-horned into the world of docker networking.
I'm not sure this is a good idea but it seems to work for now and it was fun
putting it together ;)

It's possible to remotely control a docker engine and tell it to start/stop
containers. It's not entirely uncommon to run the CI system in a VM and letting
it remotely control another docker engine can give us some flexibility in where
the CI runner is executed vs where the virtual routers are running.

libvirt can also be remotely controlled so it could potentially be used to the
same effect. However, unlike libvirt, docker also has a registry concept which
greatly simplifies the distribution of the virtual routers. It's already neatly
packaged up into a container image and now we can pull that image through a
single command. With libvirt we would need to distribute the VM image and
launch scripts as individual files.

The launch script differ from router to router. For example, it's possible to
feed a Cisco XR router a bootup config via a virtual CD-ROM drive so we can use
that to enable SSH/NETCONF and create a user. Nokia VSR however does not, so we
need to tell KVM to emulate a serial device and then have the launch script
access that virtual serial port via telnet to do the initial config.

The intention is to keep the arguments to each virtual router type as similar
as possible so that a test orchestrator or similar need minimal knowledge about
the different router types.


System requirements
-------------------
You need to run these docker images on a machine that has a docker engine and
that supports KVM, i.e. you need a Linux kernel.

Docker is available for OS X and it works by spinning up a Linux VM on top of
the xhyve hypervisor. While this means that we do have a docker engine and a
Linux kernel, we are unable to use this for vrnetlab as xhyve does not offer
nested virtualization and thus we cannot run KVM in the VM running in xhyve.

VirtualBox does not offer nested virtualization either. Parallels and VMWare
supposedely do but I don't have access to those and can't test with.

See the README file of each virtual router type for CPU, RAM and disk
requirements.


Low performance / virtual routers not starting properly
-------------------------------------------------------
If you are having problems with performance, like routers not starting or being
very slow, there are a few knobs to tweak in order to improve the situation.

The basic problem is an unfortunate combination of CPU throttling and process
scheduling causing cache thrasing which in turn leads to terrible performance.
No detailed measurements have been done to confirm this exact behaviour but the
recommended remedy has been confirmed working in multiple cases.

vrnetlab runs virtual machines using qemu/KVM, which appear just as normal
processes in Linux and are thus subject to the Linux process scheduler. If a
process wants to do work it will be scheduled to run on a core. Now, if not all
cores are used, APM will throttle down some of the cores such that the workload
can run on the remaining, say 3 out of 12 cores.  The Linux scheduler will try
to schedule processes on the cores with the higher clock speed but if you have
more VMs than cores with high clock speed than it will start moving VMs around.
L1/L2 caches are not shared by CPU cores, only L3.  Moving a process from one
core to another inevitably means that the cache is evicted. When processes are
moved around continuously we get cache thrasing and this appears to lower
performance for the VMs significantly. For some virtual routers it is to the
point where we hit various watchdog timeouts and the VMs will restart.

The very first step is to make sure you aren't trying to run too many virtual
routers on the same physical host. Some virtual routers, like Nokia SROS, has a
rather low idle CPU usage of a few percent typically. Others, like Cisco XRV9k
and Juniper vMX have a forwarding plane that is busy-looping over multiple CPU
cores, thus consuming the entire CPU core. Trying to schedule multiple such
virtual machines over the same CPU cores can lead to failure.

To improve performance, we can start by changing the CPU governor in Linux to
`performance`, for example using `cpupower frequency-set -g performance`. It
likely won't help much but try it first since it's considerably easier than the
following steps.

Disable Advanced Power Management (APM) or similar in BIOS. This will
completely prevent the CPU cores from throttling down and they will run at
their designed maximum clock frequency. This probably means turbo boost
(increasing clock frequency on a smaller subset of cores while decreasing the
frequency on remaining cores to remain at the same power and temperature
envelope) will be disabled too. Performance across all cores will however be
much more deterministic. This alone usually means that the Linux process
scheduler will now keep processes on the same cores instead of moving them
around. Before only some of the cores would run at a higher frequency and so
would be more attractive to schedule work on. With all cores at the same
frequency, there is no reason for the process scheduler to move processes
around. This removes the main cause of cache thrashing. At least that's the
simplified view of it but it appears to be working rather well in reality.

If performance is still not adequate the next step would be to disable
hyperthreading. Hyperthreading is a technology to expose two logical cores that
are executed by the same physical core. It's a strategy to avoid pipeline
stalls, essentially where the CPU waits for memory. By having two logical
threads, the CPU core can switch to the other thread whenever it needs to wait
for memory lookups. It increases total concurrent throughput, however, each
logical thread will run slower than if it had run directly on a physical CPU
core.

You can avoid the effects of hyperthreading by only scheduling your qemu
processes on half of the cores. You would need to inspect /proc/cpuinfo to
determine the exact logical core layout and make sure you only schedule
processes on one logical thread of each physical core. However, since you would
then only use half of the threads, it is easier to just disable hyperthreading
in BIOS altogether.

Applying the mentioned mitigations has so far resolved performance issues in
all cases. Report if it doesn't for you.


Docker healthcheck
-----------------
vrnetlab containers use the Docker healthcheck mechanism to report whether
they've started up properly or not.


FUAQ - Frequently or Unfrequently Asked Questions
-------------------------------------------------
##### Q: Why don't you ship pre-built docker images?
A: I don't think Cisco, Juniper or Nokia would allow me to distribute their virtual
   router images and since one of the main points of vrnetlab is to have a self
   contained docker image I don't see any other way than for you to build your
   own image based on vrnetlab but where you get to download the router image
   yourself.

##### Q: Why don't you ship docker images where I can provide the image through a volume?
A: I don't like the concept as it means you have to ship around an extra file.
   If it's a self-contained image then all you have to do is push it to your
   docker registry and then ask a box in your swarm cluster to spin it up!

##### Q: Using docker typically means no persistent storage. How is configuration persisted across restarts?
A: It is not persisted. The state of the virtual routers is lost once they are
stopped/removed. It's not possible to restart vrnetlab or at least it's not at
all tested and I don't see how it would work really. Since the primary use case
is lab / CI you should embrace the statelessness :)

##### Q: Will this consume less resources than the normal way of running XRv, vmX etc?
A: No. vrnetlab still runs KVM (in docker) to start the virtual router which
means that we will consume just as much CPU and memory, if not slightly more,
than running the router in KVM.

##### Q: If it doesn't consume less resources than KVM, why use Docker?
A: It's used primarily as a packaging format. All vrnetlab containers can be
run with similar arguments. The differences between different platforms are
effectively hidden to present a clean uniform interface. That's certainly not
true for trying to run XRv or vMX directly with qemu / virsh.

##### Q: Do you plan to support classic IOS?
A: IOS XE is available through the CSR1000v image which should satisfy all
your oldskool needs.

##### Q: How do I connect a vrnetlab router with a normal docker container?
A: I'm not entirely sure. For now you have to live with only communicating
between vrnetlab routers. There's https://github.com/TOGoS/TUN2UDP and I
suppose the same idea could be used to bridge the TCP-socket NICs used by
vrnetlab to a tun device, but if all this should happen inside a docker
container or if we should rely on setting this up on the docker host (using
something similar to pipework) is not entirely clear to me. I'll probably work
on it.

##### Q: How does this relate to GNS3, UNetLab and VIRL?
A: It was a long time since I used GNS3 and I have only briefly looked at
UNetLab and VIRL but from what I know or can see, these are all more targeted
towards interactive labbing. You get a pretty UI and similar whereas vrnetlab
is controlled in a completely programmatic fashion which makes them good at
different things. vrnetlab is superb for CI and programmatic testing where the
others probably target labs run by humans.


Building with GitLab CI
-----------------------
vrnetlab ships with a .gitlab-ci.yml config file so if you happen to be using
GitLab CI you can use this file to let your CI infrastructure build the docker
images and push them to your registry. 

GitLab features a built-in Docker registry which will be used per default - all
you need to do is enable the registry for your vrnetlab project. The necessary
information will be exposed as env vars in GitLab CI which is picked up by the
build config.

The CI runner executing the jobs must have the tag 'vrnetlab'. Make sure this
runner supports running VMs (has KVM) and allows the execution of sibling
docker containers.

If you want, you can use an external docker registry by explicitly configuring
the following environment variables:

 * DOCKER_USER - the username to authenticate to the docker registry with
 * DOCKER_PASSWORD - the password to authenticate to the docker registry with
 * DOCKER_REGISTRY - the URL to the docker registry, like reg.example.com:5000

Next you need to add the actual virtual router images to the git repository.
You can create a separate branch where you add the images as to avoid potential
git merge issues. I recommend using LFS:
```
git checkout -b images
git lfs track "*.vmdk"
git add xrv/iosxrv-k9-demo-6.0.0.vmdk .gitattributes
git commit -a -m "Added Cisco XRv 6.0.0 image"
git push your-git-repo images
```
Now CI should build the images and push to wherever $DOCKER_REGISTRY points. If
you don't want to use LFS then just skip that command.

When new changes are commited to the upstream repo/master you can just rebase
your branch on top of that:
```
git checkout master
git pull origin master
git checkout images
git rebase master
git push --force your-git-repo images
```
Note that you have to force push since you've rewritten git history.

LFS is a way to store large files with git but keeping them out of git. It's
great for the virtual router images as they never change (version is in the
filename) and so we don't really need git's version tracking for them. LFS is
considerably faster than plain git. For very large files it is possible to run
into LFS timeouts, try setting:
```
git config lfs.dialtimeout 60
```

Building with GitHub Actions
----------------------------

vrnetlab ships with a .github/workflows/test.yml config file which is primarily
used in the public upstream repository: https://github.com/vrnetlab/vrnetlab.

The GitHub Actions runner must support running VMs (has KVM) and allows the
execution of sibling docker containers. The first requirement is not met by the
free GitHub Actions runners, so we use a self-hosted runner for the VM test
(thanks [GleSYS](https://glesys.com/) for sponsoring the runner ❤️).

This also solves the issue where to the public nature of the repository we
cannot include the actual virtual router images in public repository via Git
LFS. Instead, the images are provided to the build container via a local bind
volume mount. This means the router images must be available on the host machine
where the build is running. The images are mounted into the build container at
`/vrnetlab-images`.

The self-hosted GitHub Actions runner was set up on a machine using the
instructions here:
https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners
We then create a script that reads in the `VRNETLAB_IMAGES` environment variable
(set up as a repository variable) and creates a named docker volume
*vrnetlab-images* that bind mounts the host path provided in the variable:

```
$ cat create-vrnetlab-images-volume.sh
docker volume create --opt o=bind --opt type=none --opt device=${VRNETLAB_IMAGES} vrnetlab-images
docker volume inspect vrnetlab-images
```

Then in the runners `.env` file, we instruct the runner to run a script on job
startup to create the volume:

```
ACTIONS_RUNNER_HOOK_JOB_STARTED=/path/to/runner/create-vrnetlab-images-volume.sh
```

The job container can then mount this volume and access the images in
`/vrnetlab-images` regardless of the host path.:

```yaml
  test-vr:
    runs-on: ["self-hosted"]
    container:
      image: vrnetlab/ci-builder
      volumes:
        - vrnetlab-images:/vrnetlab-images
```