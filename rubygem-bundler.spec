%{?scl:%scl_package rubygem-%{gem_name}}
%{!?scl:%global pkg_name %{name}}

%global gem_name bundler

%{!?enable_test: %global enable_test 0}

Summary: Library and utilities to manage a Ruby application's gem dependencies
Name: %{?scl_prefix}rubygem-%{gem_name}
Version: 1.10.6
Release: 3%{?dist}
Group: Development/Languages
License: MIT
URL: http://gembundler.com
Source0: http://rubygems.org/gems/%{gem_name}-%{version}.gem
# git clone https://github.com/bundler/bundler.git && cd bundler
# git checkout v1.10.6 && tar czvf bundler-1.10.6-specs.tgz spec/
Source1: %{gem_name}-%{version}-specs.tgz
Requires: %{?scl_prefix_ruby}ruby(release)
Requires: %{?scl_prefix_ruby}ruby(rubygems)
%{?scl:BuildRequires: scldevel(ruby)}
BuildRequires: %{?scl_prefix_ruby}ruby(release)
BuildRequires: %{?scl_prefix_ruby}rubygems-devel
BuildRequires: %{?scl_prefix_ruby}ruby
%if 0%{enable_test} > 0
BuildRequires: %{?scl_prefix_ruby}ruby-devel
BuildRequires: %{?scl_prefix}rubygem(rspec)
BuildRequires: git
%endif
# https://github.com/bundler/bundler/issues/3647
Provides: %{?scl_prefix}bundled(rubygem(molinillo)) = 0.2.3
Provides: %{?scl_prefix}bundled(rubygem-molinillo) = 0.2.3
Provides: %{?scl_prefix}bundled(rubygem(net-http-persisntent)) = 2.9.3
Provides: %{?scl_prefix}bundled(rubygem-net-http-persisntent) = 2.9.3
Provides: %{?scl_prefix}bundled(rubygem(thor)) = 0.19.1
Provides: %{?scl_prefix}bundled(rubygem-thor) = 0.19.1
BuildArch: noarch
Provides: %{?scl_prefix}rubygem(%{gem_name}) = %{version}

%description
Bundler manages an application's dependencies through its entire life, across
many machines, systematically and repeatably.

%package doc
Summary: Documentation for %{pkg_name}
Group: Documentation
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{pkg_name}.

%prep
%setup -q -c -T
%{?scl:scl enable %{scl} - << \EOF}
%gem_install -n %{SOURCE0}
%{?scl:EOF}

%build

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/

mkdir -p %{buildroot}/%{_bindir}
cp -a .%{_bindir}/* \
        %{buildroot}%{_bindir}/

find %{buildroot}%{gem_instdir}/bin -type f | xargs chmod a+x
find %{buildroot}%{gem_instdir}/lib/bundler/templates/newgem/bin -type f | xargs chmod 755
chmod 755 %{buildroot}%{gem_instdir}/lib/bundler/templates/Executable*

# Man pages are used by Bundler internally, do not remove them!
mkdir -p %{buildroot}%{_mandir}/man5
cp -a %{buildroot}%{gem_libdir}/bundler/man/gemfile.5 %{buildroot}%{_mandir}/man5
mkdir -p %{buildroot}%{_mandir}/man1
for i in bundle bundle-config bundle-exec bundle-install bundle-package bundle-platform bundle-update
do
        cp -a %{buildroot}%{gem_libdir}/bundler/man/$i %{buildroot}%{_mandir}/man1/`echo $i.1`
done

# Test suite has to be disabled for official build, since it downloads various
# gems, which are not in Fedora or they have different version etc.
# Nevertheless, the test suite should run for local builds.
%if 0%{enable_test} > 0

%check
pushd .%{gem_instdir}

tar xzvf %{SOURCE1}

# This test does not work, since ruby is configured with --with-ruby-version=''
# https://github.com/bundler/bundler/issues/2365
sed -i '/"fetches gems again after changing the version of Ruby"/,/end$/{s/^/#/}' spec/install/gems/platform_spec.rb

# Test suite needs to run in initialized git repository.
# https://github.com/carlhuda/bundler/issues/2022
git init

%{?scl:scl enable %{scl} - << \EOF}
rspec spec
%{?scl:EOF}

%endif

%files
%dir %{gem_instdir}
%{_bindir}/bundle
%{_bindir}/bundler
%exclude %{gem_instdir}/.*
%exclude %{gem_libdir}/bundler/ssl_certs/.document
%exclude %{gem_libdir}/bundler/ssl_certs/*.pem
%license %{gem_instdir}/LICENSE.md
%{gem_instdir}/bin
%{gem_libdir}
%exclude %{gem_instdir}/man
%exclude %{gem_cache}
%{gem_spec}
%doc %{_mandir}/man1/*
%doc %{_mandir}/man5/*

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/CHANGELOG.md
%doc %{gem_instdir}/CODE_OF_CONDUCT.md
%doc %{gem_instdir}/ISSUES.md
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/CONTRIBUTING.md
%doc %{gem_instdir}/DEVELOPMENT.md
%{gem_instdir}/Rakefile
%{gem_instdir}/%{gem_name}.gemspec

%changelog
* Wed Feb 17 2016 Pavel Valena <pvalena@redhat.com> - 1.10.6-3
- Add scl macros

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Oct 12 2015 Vít Ondruch <vondruch@redhat.com> - 1.10.6-1
- Update to Bundler 1.10.6.
- Keep vendored libraries.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Feb 05 2015 Vít Ondruch <vondruch@redhat.com> - 1.7.8-2
- Properly uninstall the vendor directory.

* Tue Dec 09 2014 Vít Ondruch <vondruch@redhat.com> - 1.7.8-1
- Update to Bundler 1.7.8.

* Thu Nov 20 2014 Josef Stribny <jstribny@redhat.com> - 1.7.6-2
- Keep ssl_certs/certificate_manager.rb file (used in tests)
- Correctly add load paths for gems during tests

* Wed Nov 12 2014 Josef Stribny <jstribny@redhat.com> - 1.7.6-1
- Update to 1.7.6

* Tue Nov 11 2014 Josef Stribny <jstribny@redhat.com> - 1.7.4-2
- Use symlinks for vendored libraries (rhbz#1163039)

* Mon Oct 27 2014 Vít Ondruch <vondruch@redhat.com> - 1.7.4-1
- Update to Bundler 1.7.4.
- Add thor and net-http-persistent dependencies into .gemspec.

* Mon Sep 22 2014 Josef Stribny <jstribny@redhat.com> - 1.7.3-1
- Update to 1.7.3

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Jan 12 2014 Sam Kottler <skottler@fedoraproject.org> - 1.5.2-1
- Update to 1.5.2 (BZ #1047222)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun 11 2013 Vít Ondruch <vondruch@redhat.com> - 1.3.5-1
- Update to Bundler 1.3.5.

* Mon Mar 04 2013 Josef Stribny <jstribny@redhat.com> - 1.3.1-1
- Rebuild for https://fedoraproject.org/wiki/Features/Ruby_2.0.0
- Update to Bundler 1.3.1

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Nov 02 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.1-1
- Update to Bundler 1.2.1.
- Fix permissions on some executable files.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Vít Ondruch <vondruch@redhat.com> - 1.1.4-1
- Update to Bundler 1.1.4.

* Wed Feb 01 2012 Vít Ondruch <vondruch@redhat.com> - 1.0.21-1
- Rebuilt for Ruby 1.9.3.
- Update to Bundler 1.0.21.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Jul 07 2011 Vít Ondruch <vondruch@redhat.com> - 1.0.15-1
- Updated to Bundler 1.0.15

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb 04 2011 Vít Ondruch <vondruch@redhat.com> - 1.0.10-1
- Upstream update

* Thu Jan 27 2011 Vít Ondruch <vondruch@redhat.com> - 1.0.9-2
- More concise summary
- Do not remove manpages, they are used internally
- Added buildroot cleanup in clean section

* Mon Jan 24 2011 Vít Ondruch <vondruch@redhat.com> - 1.0.9-1
- Bumped to Bundler 1.0.9
- Installed manual pages
- Removed obsolete buildroot cleanup

* Mon Nov 1 2010 Jozef Zigmund <jzigmund@redhat.com> - 1.0.3-2
- Add ruby(abi) dependency
- Add using macro %%{geminstdir} in files section
- Add subpackage doc for doc files
- Removed .gitignore file
- Removed rubygem-thor from vendor folder
- Add dependency rubygem(thor)

* Mon Oct 18 2010 Jozef Zigmund <jzigmund@redhat.com> - 1.0.3-1
- Initial package
