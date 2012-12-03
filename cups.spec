Summary:	Common Unix Printing System
Name:		cups
Version:	1.6.1
Release:	4
Epoch:		1
License:	GPL/LGPL
Group:		Applications/Printing
Source0:	http://ftp.easysw.com/pub/cups/%{version}/%{name}-%{version}-source.tar.bz2
# Source0-md5:	87ade07e3d1efd03c9c3add949cf9c00
Source1:	%{name}.pamd
Source2:	%{name}.logrotate
Source3:	%{name}-modprobe.conf
Source4:	%{name}-tmpfiles.conf
Patch0:		%{name}-config.patch
Patch1:		%{name}-options.patch
Patch2:		%{name}-man_pages_linking.patch
Patch3:		%{name}-nostrip.patch
Patch4:		%{name}-certs_FHS.patch
Patch5:		%{name}-peercred.patch
#
# http://www.cups.org/str.php?L4156
Patch10:	%{name}-avahi-missing-in-conditionals.patch
# http://www.cups.org/str.php?L4157
Patch11:	%{name}-conf-remove-obsolete-browse-directives.patch
Patch12:	%{name}-no-export-ssllibs.patch
# http://www.cups.org/str.php?L4158
Patch13:	%{name}-recognize-remote-cups-queue-via-dnssd-uri.patch
# http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/net-print/cups/files/cups-1.5.0-systemd-socket.patch?revision=1.1
Patch14:	%{name}-systemd-socket.patch
# http://cups.org/str.php?L4155
Patch15:	%{name}-usb-backend-reset-after-job-only-for-specific-devices.patch
Patch16:	%{name}-default-error-policy-retry-job.patch
Patch17:	%{name}-default-log-settings.patch
URL:		http://www.cups.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	dbus-devel
BuildRequires:	gnutls-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libtiff-devel
BuildRequires:	pam-devel
BuildRequires:	pkg-config
Requires(post,preun,postun):	systemd-units
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_ulibdir	%{_prefix}/lib

%description
CUPS provides a portable printing layer for UNIX-based operating
systems. It has been developed by Easy Software Products to promote a
standard printing solution for all UNIX vendors and users. CUPS
provides the System V and Berkeley command-line interfaces. CUPS uses
the Internet Printing Protocol ("IPP") as the basis for managing print
jobs and queues. The Line Printer Daemon ("LPD") Server Message Block
("SMB"), and AppSocket (a.k.a. JetDirect) protocols are also supported
with reduced functionality. CUPS adds network printer browsing and
PostScript Printer Description ("PPD") based printing options to
support real-world printing under UNIX.

%package lib
Summary:	Common Unix Printing System Libraries
Group:		Libraries
Provides:	%{name}-libs = %{epoch}:%{version}-%{release}

%description lib
Common Unix Printing System Libraries.

%package clients
Summary:	Common Unix Printing System Clients
Group:		Applications/Printing
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}

%description clients
Common Unix Printing System Clients.

%package image-lib
Summary:	Common Unix Printing System Libraries - images manipulation
Group:		Libraries
Requires:	%{name}-lib = %{epoch}:%{version}-%{release}

%description image-lib
Common Unix Printing System Libraries - images manupalation.

%package devel
Summary:	Common Unix Printing System development files
Group:		Development/Libraries
Requires:	%{name}-image-lib = %{epoch}:%{version}-%{release}
Requires:	%{name}-lib = %{epoch}:%{version}-%{release}
Requires:	gnutls-devel

%description devel
Common Unix Printing System development files.
CUPS.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p0
%patch16 -p1
%patch17 -p1

sed -i -e 's|.SILENT:.*||g' Makedefs.in

%build
%{__aclocal} -I config-scripts
%{__autoconf}
%configure \
	--disable-cdsassl				\
	--disable-ldap					\
	--enable-dbus					\
	--enable-gnutls					\
	--enable-pam					\
	--enable-raw-printing				\
	--enable-shared					\
	--enable-ssl					\
	--enable-threads				\
	--libdir=%{_ulibdir}				\
	--with-cups-group=lp				\
	--with-cups-user=lp				\
	--with-dbusdir=/etc/dbus-1			\
	--with-docdir=%{_ulibdir}/%{name}/cgi-bin	\
	--with-optim="%{rpmcflags}"			\
	--with-printcap=/etc/printcap			\
	--with-system-groups=sys			\
	--with-systemdsystemunitdir=%{systemdunitdir}	\
	--without-java					\
	--without-perl					\
	--without-php					\
	--without-python
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{pam.d,logrotate.d}	\
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}		\
	$RPM_BUILD_ROOT/etc/modprobe.d			\
	$RPM_BUILD_ROOT/var/log/{,archive/}cups		\
	$RPM_BUILD_ROOT%{_datadir}/cups/charsets

%{__make} install \
	BUILDROOT=$RPM_BUILD_ROOT	\
	CUPS_USER=$(id -u)		\
	CUPS_GROUP=$(id -g)

if [ "%{_lib}" != "lib" ] ; then
	install -d $RPM_BUILD_ROOT%{_libdir}
	mv $RPM_BUILD_ROOT%{_ulibdir}/*.so* $RPM_BUILD_ROOT%{_libdir}
fi

install %{SOURCE1} $RPM_BUILD_ROOT/etc/pam.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/modprobe.d/cups.conf
install %{SOURCE4} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/cups.conf

touch $RPM_BUILD_ROOT/var/log/cups/{access_log,error_log,page_log}
touch $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/{classes,printers,client}.conf

# windows drivers can be put there.
install -d $RPM_BUILD_ROOT%{_datadir}/cups/drivers

# dirs for gimp-print-cups-4.2.7-1
install -d $RPM_BUILD_ROOT%{_datadir}/cups/model/{C,da,en_GB,fr,nb,pl,sv}

touch $RPM_BUILD_ROOT/var/cache/cups/help.index
touch $RPM_BUILD_ROOT/var/cache/cups/{job,remote}.cache
touch $RPM_BUILD_ROOT/var/cache/cups/ppds.dat
install -d $RPM_BUILD_ROOT%{_sysconfdir}/cups/ssl

# check-files cleanup
rm -rf $RPM_BUILD_ROOT%{_mandir}/{,es/,fr/}cat?
rm -rf $RPM_BUILD_ROOT/etc/rc.d
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/cupsd.conf.default

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post cups.service

%preun
%systemd_preun cups.service

%postun
%systemd_postun

%post	lib -p /usr/sbin/ldconfig
%postun	lib -p /usr/sbin/ldconfig

%post	image-lib -p /usr/sbin/ldconfig
%postun	image-lib -p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc *.txt
%attr(4755,lp,root) %{_bindir}/lppasswd
%attr(600,root,lp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/classes.conf
%attr(600,root,lp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/printers.conf
%attr(600,root,lp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/snmp.conf
%attr(640,root,lp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/cupsd.conf

%attr(640,root,root) %config %verify(not md5 mtime size) /etc/pam.d/cups
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}

%attr(755,root,root) %{_bindir}/cupstestdsc
%attr(755,root,root) %{_bindir}/cupstestppd
%attr(755,root,root) %{_bindir}/ipptool
%attr(755,root,root) %{_bindir}/ppd*

%attr(755,root,root) %{_sbindir}/cupsctl
%attr(755,root,root) %{_sbindir}/cupsd
%attr(755,root,root) %{_sbindir}/cupsfilter

%dir %attr(700,root,lp) %{_sysconfdir}/%{name}/ssl
%dir %attr(755,root,lp) %{_sysconfdir}/%{name}/ppd
%dir %{_sysconfdir}/%{name}/interfaces

/etc/dbus-1/system.d/cups.conf
%{systemdunitdir}/*.path
%{systemdunitdir}/*.service
%{systemdunitdir}/*.socket
%{systemdtmpfilesdir}/cups.conf

%dir %{_ulibdir}/cups
%dir %{_ulibdir}/cups/*

%attr(755,root,root) %{_ulibdir}/cups/cgi-bin/*.cgi
%{_ulibdir}/cups/cgi-bin/*.css
%{_ulibdir}/cups/cgi-bin/*.html
%{_ulibdir}/cups/cgi-bin/*.txt
%{_ulibdir}/cups/cgi-bin/help
%{_ulibdir}/cups/cgi-bin/images

%lang(ca) %{_ulibdir}/cups/cgi-bin/ca
%lang(es) %{_ulibdir}/cups/cgi-bin/es
%lang(ja) %{_ulibdir}/cups/cgi-bin/ja

%dir %{_datadir}/cups/templates
%{_datadir}/cups/templates/*.tmpl
%lang(ca) %{_datadir}/cups/templates/ca
%lang(es) %{_datadir}/cups/templates/es
%lang(ja) %{_datadir}/cups/templates/ja

%dir %{_datadir}/cups/model
%dir %{_datadir}/cups/model/C
%lang(da) %dir %{_datadir}/cups/model/da
%lang(en_GB) %dir %{_datadir}/cups/model/en_GB
%lang(fr) %dir %{_datadir}/cups/model/fr
%lang(nb) %dir %{_datadir}/cups/model/nb
%lang(pl) %dir %{_datadir}/cups/model/pl
%lang(sv) %dir %{_datadir}/cups/model/sv

%attr(755,root,root) %{_ulibdir}/cups/backend/*
%{_sysconfdir}/modprobe.d/cups.conf

%attr(755,root,root) %{_ulibdir}/cups/daemon/cups-deviced
%attr(755,root,root) %{_ulibdir}/cups/daemon/cups-driverd
%attr(755,root,root) %{_ulibdir}/cups/daemon/cups-exec
%attr(755,root,root) %{_ulibdir}/cups/daemon/cups-lpd
%attr(755,root,root) %{_ulibdir}/cups/filter/*
%attr(755,root,root) %{_ulibdir}/cups/monitor/*
%attr(755,root,root) %{_ulibdir}/cups/notifier/*

%{_datadir}/cups/banners
%{_datadir}/cups/charsets
%{_datadir}/cups/data
%{_datadir}/cups/drivers
%{_datadir}/cups/drv
%{_datadir}/cups/examples
%{_datadir}/cups/ipptool
%{_datadir}/cups/mime
%{_datadir}/cups/ppdc

%{_mandir}/man1/cupstestdsc.1*
%{_mandir}/man1/cupstestppd.1*
%{_mandir}/man1/ipptool.1*
%{_mandir}/man1/lppasswd.1*
%{_mandir}/man1/ppd*.1*
%{_mandir}/man5/*
%{_mandir}/man7/backend.7*
%{_mandir}/man7/filter.7*
%{_mandir}/man7/notifier.7*
%{_mandir}/man8/accept.8*
%{_mandir}/man8/cups-deviced.8*
%{_mandir}/man8/cups-driverd.8*
%{_mandir}/man8/cups-lpd.8*
%{_mandir}/man8/cups-snmp.8*
%{_mandir}/man8/cupsaddsmb.8*
%{_mandir}/man8/cupsctl.8*
%{_mandir}/man8/cupsd.8*
%{_mandir}/man8/cupsenable.8*
%{_mandir}/man8/cupsfilter.8*
%{_mandir}/man8/lp*

%dir %attr(775,root,lp) /var/cache/cups
%dir %attr(755,root,lp) /var/lib/cups
%dir %attr(511,lp,sys) /var/lib/cups/certs
%dir %attr(710,root,lp) /var/spool/cups
%dir %attr(1770,root,lp) /var/spool/cups/tmp

%attr(600,lp,lp) %ghost /var/cache/cups/help.index
%attr(640,root,lp) %ghost /var/cache/cups/job.cache
%attr(600,lp,lp) %ghost /var/cache/cups/ppds.dat
%attr(640,root,lp) %ghost /var/cache/cups/remote.cache
%attr(750,root,logs) %dir /var/log/archive/cups
%attr(750,root,logs) %dir /var/log/cups
%attr(640,root,logs) %ghost /var/log/cups/access_log
%attr(640,root,logs) %ghost /var/log/cups/error_log
%attr(640,root,logs) %ghost /var/log/cups/page_log

%lang(ca) %{_datadir}/locale/ca/cups_ca.po
%lang(es) %{_datadir}/locale/es/cups_es.po
%lang(ja) %{_datadir}/locale/ja/cups_ja.po

%files lib
%defattr(644,root,root,755)
%dir %attr(755,root,lp) %{_sysconfdir}/%{name}
%attr(755,root,root) %{_libdir}/libcups.so.*
%attr(755,root,root) %{_libdir}/libcupscgi.so.*
%attr(755,root,root) %{_libdir}/libcupsmime.so.*
%attr(755,root,root) %{_libdir}/libcupsppdc.so.*
%dir %{_datadir}/cups

%files clients
%defattr(644,root,root,755)
%attr(644,root,lp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/client.conf
%attr(755,root,root) %{_bindir}/cancel
%attr(755,root,root) %{_bindir}/lp
%attr(755,root,root) %{_bindir}/lpoptions
%attr(755,root,root) %{_bindir}/lpq
%attr(755,root,root) %{_bindir}/lpr
%attr(755,root,root) %{_bindir}/lprm
%attr(755,root,root) %{_bindir}/lpstat
%attr(755,root,root) %{_sbindir}/accept
%attr(755,root,root) %{_sbindir}/cupsaccept
%attr(755,root,root) %{_sbindir}/cupsaddsmb
%attr(755,root,root) %{_sbindir}/cupsenable
%attr(755,root,root) %{_sbindir}/cupsdisable
%attr(755,root,root) %{_sbindir}/cupsreject
%attr(755,root,root) %{_sbindir}/lpadmin
%attr(755,root,root) %{_sbindir}/lpc
%attr(755,root,root) %{_sbindir}/lpinfo
%attr(755,root,root) %{_sbindir}/lpmove
%attr(755,root,root) %{_sbindir}/reject

%{_mandir}/man1/cancel.1*
%{_mandir}/man1/lp.1*
%{_mandir}/man1/lpoptions.1*
%{_mandir}/man1/lpq.1*
%{_mandir}/man1/lpr.1*
%{_mandir}/man1/lprm.1*
%{_mandir}/man1/lpstat.1*
%{_mandir}/man8/cupsaccept.8*
%{_mandir}/man8/cupsdisable.8*
%{_mandir}/man8/cupsreject.8*
%{_mandir}/man8/reject.8*

%files image-lib
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcupsimage.so.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cups-config
%attr(755,root,root) %{_libdir}/libcups.so
%attr(755,root,root) %{_libdir}/libcupscgi.so
%attr(755,root,root) %{_libdir}/libcupsimage.so
%attr(755,root,root) %{_libdir}/libcupsmime.so
%attr(755,root,root) %{_libdir}/libcupsppdc.so
%{_includedir}/cups
%{_mandir}/man1/cups-config*

