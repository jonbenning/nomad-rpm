%if 0%{?_version:1}
%define         _verstr      %{_version}
%else
%define         _verstr      0.5.6
%endif

Name:           nomad
Version:        %{_verstr}
Release:        1%{?dist}
Summary:        Nomad is a tool for managing a cluster of machines and running applications on them.

Group:          System Environment/Daemons
License:        MPLv2.0
URL:            http://www.nomadproject.io
Source0:        https://releases.hashicorp.com/%{name}/%{version}/%{name}_%{version}_linux_amd64.zip
Source1:        %{name}.sysconfig
Source2:        %{name}.service
Source3:        %{name}.init
Source4:        %{name}.json
Source5:        %{name}.logrotate
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
BuildRequires:  systemd-units
Requires:       systemd
%else
Requires:       logrotate
%endif
Requires(pre): shadow-utils

%description

Nomad is a tool for managing a cluster of machines and running applications on them. Nomad abstracts away machines and the location of applications, and instead enables users to declare what they want to run and Nomad handles where they should run and how to run them.

The key features of Nomad are:

 - Docker Support: Nomad supports Docker as a first-class workload type. Jobs submitted to Nomad can use the docker driver to easily deploy containerized applications to a cluster. Nomad enforces the user-specified constraints, ensuring the application only runs in the correct region, datacenter, and host environment. Jobs can specify the number of instances needed and Nomad will handle placement and recover from failures automatically.

 - Operationally Simple: Nomad ships as a single binary, both for clients and servers, and requires no external services for coordination or storage. Nomad combines features of both resource managers and schedulers into a single system. Nomad builds on the strength of Serf and Consul, distributed management tools by HashiCorp.

 - Multi-Datacenter and Multi-Region Aware: Nomad models infrastructure as groups of datacenters which form a larger region. Scheduling operates at the region level allowing for cross-datacenter scheduling. Multiple regions federate together allowing jobs to be registered globally.

 - Flexible Workloads: Nomad has extensible support for task drivers, allowing it to run containerized, virtualized, and standalone applications. Users can easily start Docker containers, VMs, or application runtimes like Java. Nomad supports Linux, Windows, BSD and OSX, providing the flexibility to run any workload.

 - Built for Scale: Nomad was designed from the ground up to support global scale infrastructure. Nomad is distributed and highly available, using both leader election and state replication to provide availability in the face of failures. Nomad is optimistically concurrent, enabling all servers to participate in scheduling decisions which increases the total throughput and reduces latency to support demanding workloads.

%prep
%setup -q -c -b 0

%install
mkdir -p %{buildroot}/%{_bindir}
cp nomad %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}.d
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}.d/example
cp %{SOURCE4} %{buildroot}/%{_sysconfdir}/%{name}.d/example/%{name}.json
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
cp %{SOURCE1} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
mkdir -p %{buildroot}/%{_unitdir}
cp %{SOURCE2} %{buildroot}/%{_unitdir}/
%else
mkdir -p %{buildroot}/%{_initrddir}
mkdir -p %{buildroot}/%{_sysconfdir}/logrotate.d
cp %{SOURCE3} %{buildroot}/%{_initrddir}/nomad
cp %{SOURCE5} %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}
%endif

%pre
getent group nomad >/dev/null || groupadd -r nomad
getent passwd nomad >/dev/null || \
    useradd -r -g nomad -d /var/lib/nomad -s /sbin/nologin \
    -c "nomadproject.io user" nomad
exit 0

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service
%else
%post
/sbin/chkconfig --add %{name}

%preun
if [ "$1" = 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%dir %attr(750, root, nomad) %{_sysconfdir}/%{name}.d
%dir %attr(750, root, nomad) %{_sysconfdir}/%{name}.d/example
%attr(750, root, nomad) %{_sysconfdir}/%{name}.d/example/%{name}.json
%dir %attr(750, nomad, nomad) %{_sharedstatedir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
%{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}
%{_sysconfdir}/logrotate.d/%{name}
%endif
%attr(755, root, root) %{_bindir}/nomad

%doc

%changelog
* Wed May 3 2017 jb <jon.benning@gmail.com>
- Convert consul-rpm for use with Nomad 
- vers 0.5.6
