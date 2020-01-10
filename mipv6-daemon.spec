Name:		mipv6-daemon
Epoch:		2
Version:	1.0
Release:	2%{?dist}
Summary:	Mobile IPv6 (MIPv6) Daemon

Group:		System Environment/Daemons
License:	GPLv2
URL:		http://www.umip.org/
Source0:	http://people.redhat.com/tgraf/mipv6-daemon/mipv6-daemon-%{version}.tar.gz
Source1:	mip6d.init
Source2:	mip6d.sysconfig
Source3:	mip6d.conf
Patch1: 0001-rh804124_write_garbage_to_netlink_socket.patch
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	flex bison indent
Requires:	initscripts, chkconfig

%description
The mobile IPv6 daemon allows nodes to remain
reachable while moving around in the IPv6 Internet.

%prep
%setup -q -n umip-%{version}

%patch1 -p1 -b .0001-rh804124_write_garbage_to_netlink_socket.orig

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_initrddir}
install -m755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/mip6d
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mip6d
install -m644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/mip6d.conf

%clean
rm -rf $RPM_BUILD_ROOT

%preun
if [ "$1" = 0 ]
then
	/sbin/service mip6d stop > /dev/null 2>&1 ||:
	/sbin/chkconfig --del mip6d
fi

%post
/sbin/chkconfig --add mip6d

%postun
if [ "$1" -ge "1" ]; then
	/sbin/service mip6d condrestart > /dev/null 2>&1 ||:
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING NEWS README README.IPsec THANKS extras
%{_initrddir}/mip6d
%config(noreplace) %{_sysconfdir}/sysconfig/mip6d
%config(noreplace) %{_sysconfdir}/mip6d.conf
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man7/*

%changelog
* Fri Jul 18 2014 Thomas Haller <thaller@redhat.com> - 2:1.0-2
* fix writing garbage to netlink socket (rh #804124)

* Wed May 7 2014 Thomas Graf <tgraf@redhat.com> - 2:1.0-1
- Update to umip 1.0
* Thu Feb 03 2011 Thomas Graf <tgraf at, redhat.com> 2.0.2.20100203bgit-1
- Move to umip.org codebase (head: 6232b73e869a589a9eea22653929ab670eb0c6bb)
* Thu Jul 15 2010 Thomas Graf <tgraf at, redhat.com> 0.4-5
- Fix CVE-2010-2522 and CVE-2010-2523 by including the patches:
  - Additional sanity checks for ND options length
  - Security fix: Check origin of netlink messages in netlink helpers.
* Mon Jul 5 2010 Thomas Graf <tgraf at, redhat.com> 0.4-4
- Fixed initscript according to SysVInitScript guidelines:
    - Corrected usage text
    - Added force-reload, condrestart and try-restart actions
    - Fixed return code of status action
    - Only start/stop daemon if not already running/stopped
* Thu May 20 2010 Thomas Graf <tgraf at, redhat.com> 0.4-3
- Inclusion of NEPL patch (NEMO support)
* Mon Aug 17 2009 Thomas Graf <tgraf at, redhat.com> 0.4-1
- initial package release
