Name:		mipv6-daemon
Epoch:		2
Version:	1.0
Release:	3%{?dist}
Summary:	Mobile IPv6 (MIPv6) Daemon

Group:		System Environment/Daemons
License:	GPLv2
URL:		http://www.umip.org/
Source0:	http://people.redhat.com/tgraf/mipv6-daemon/mipv6-daemon-%{version}.tar.gz
Source1:	mip6d.service
Source2:	mip6d.sysconfig
Source3:	mip6d.conf
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires: flex >= 2.5.31
BuildRequires: bison indent systemd-units

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

# For triggerun
Requires(post): systemd-sysv

%description
The mobile IPv6 daemon allows nodes to remain
reachable while moving around in the IPv6 Internet.

%prep
%setup -q -n umip-%{version}

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_unitdir}
install -m644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/mip6d.service
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mip6d
install -m644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/mip6d.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if 0%{?systemd_post:1}
    %systemd_post %{name}.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%preun
%if 0%{?systemd_preun:1}
    %systemd_preun %{name}.service
%else
    if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
        /bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
        /bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
    fi
%endif

%postun
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart %{name}.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
    # Package upgrade, not uninstall
        /bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
    fi
%endif

%triggerun -- mipv6-daemon < 2.0.2.20110203bgit-4
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply mip6d
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save mip6d >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del mip6d >/dev/null 2>&1 || :
/bin/systemctl try-restart mip6d.service >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING NEWS README README.IPsec THANKS extras
%{_unitdir}/mip6d.service
%config(noreplace) %{_sysconfdir}/sysconfig/mip6d
%config(noreplace) %{_sysconfdir}/mip6d.conf
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man7/*

%changelog
* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 2:1.0-3
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2:1.0-2
- Mass rebuild 2013-12-27

* Tue Jul 02 2013 Thomas Graf <tgraf@redhat.com> - 1.0-2
- Update to umip 1.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2.20121118git-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov 20 2012 Thomas Graf <tgraf@fedoraproject.org> 2.0.2.20121118-2
- Scriptlets replaced with new systemd macros (#850209)

* Sun Nov 18 2012 Thomas Graf <tgraf@fedoraproject.org> 2.0.2.20121118-1
- Update to umip.git HEAD 74528e1ffd2ecdd31e1a17f9d9ade530a86632fd

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2.20110203bgit-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr 25 2012 Jon Ciesla <limburgher@gmail.com> - 2.0.2.20110203bgit-4
- Migrate to systemd, BZ 789773.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2.20110203bgit-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2.20110203bgit-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Feb 03 2011 Thomas Graf <tgraf at, redhat.com> 2.0.2.20100203bgit-1
- Can't use autoreconf
* Thu Feb 03 2011 Thomas Graf <tgraf at, redhat.com> 2.0.2.20100203git-1
- Move to umip.org codebase (head: 6232b73e869a589a9eea22653929ab670eb0c6bb)
* Wed Jul 14 2010 Thomas Graf <tgraf at, redhat.com> 0.4-5
- Fix CVE-2010-2522 and CVE-2010-2523 by including the patches:
  - Additional sanity checks for ND options length
  - Security fix: Check origin of netlink messages in netlink helpers.
* Tue May 25 2010 Thomas Graf <tgraf at, redhat.com> 0.4-4
- Fixed initscript according to SysVInitScript guidelines:
    - Corrected usage text
    - Added force-reload, condrestart and try-restart actions
    - Fixed return code of status action
    - Only start/stop daemon if not already running/stopped
* Wed Mar 24 2010 Thomas Graf <tgraf at, redhat.com> 0.4-2
- Inclusion of NEPL patch (NEMO support)
* Mon Aug 17 2009 Thomas Graf <tgraf at, redhat.com> 0.4-1
- initial package release
