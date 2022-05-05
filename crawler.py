# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import os, requests, re, datetime, argparse

def alpine_crawler(root_path):
    alpineMatrix = {
        "main": ["v3.15", "v3.14", "v3.13", "v3.12", "v3.11", "v3.10", "v3.9", "v3.8", "v3.7", "v3.6", "v3.5", "v3.4", "v3.3"],
        "community": ["v3.15", "v3.14", "v3.13", "v3.12", "v3.11", "v3.10", "v3.9", "v3.8", "v3.7", "v3.6", "v3.5", "v3.4", "v3.3"]
    }

    alpineDbURL = "https://secdb.alpinelinux.org/%s/%s.json"

    for repo in alpineMatrix.keys():
        for release in alpineMatrix[repo]:
            target_dirpath = os.path.join(root_path, "alpine", release)
            if not os.path.exists(target_dirpath):
                os.makedirs(target_dirpath)
            
            json_url = alpineDbURL % (release, repo)

            try:
                res = requests.get(json_url)
                if res.status_code == 200:
                    with open(os.path.join(target_dirpath, "%s.json" % repo), "wb") as f:
                        f.write(res.content)
                else:
                    print("ERROR: failed to download %s, status code: %d" % (json_url, res.status_code))
            except:
                print("EXCEPTION: failed to download %s" % json_url)

def amazon_crawler(root_path):
    awsMatrix = {
        "linux1": "http://repo.us-west-2.amazonaws.com/2018.03/updates/x86_64/mirror.list",
        "linux2": "https://cdn.amazonlinux.com/2/core/latest/x86_64/mirror.list"
    }

    for release in awsMatrix.keys():
        try:
            res = requests.get(awsMatrix[release])
            if res.status_code == 200:
                mirror_url = res.text.strip()
                if re.match(r'^https?:/{2}\w.+$', mirror_url):
                    target_dirpath = os.path.join(root_path, "amazon", release, "repodata")
                    if not os.path.exists(target_dirpath):
                        os.makedirs(target_dirpath)
                    
                    xml_url = mirror_url + "/repodata/repomd.xml"
                    gz_url = mirror_url + "/repodata/updateinfo.xml.gz"

                    try:
                        res = requests.get(xml_url)
                        if res.status_code == 200:
                            with open(os.path.join(target_dirpath, "repomd.xml"), "wb") as f:
                                f.write(res.content)
                        else:
                            print("ERROR: failed to download %s repomd.xml, status code: %d" % (release, res.status_code))
                    except:
                        print("EXCEPTION: failed to download %s repomd.xml" % release)
                    
                    try:
                        res= requests.get(gz_url)
                        if res.status_code == 200:
                            with open(os.path.join(target_dirpath, "updateinfo.xml.gz"), "wb") as f:
                                f.write(res.content)
                        else:
                            print("ERROR: failed to download %s updateinfo.xml.gz, status code: %d" % (release, res.status_code))
                    except:
                        print("EXCEPTION: failed to download %s updateinfo.xml.gz" % release)
                else:
                    print("ERROR: malformed mirror url: %s" % mirror_url)
            else: 
                print("ERROR: failed to download %s mirror list, status code: %d" % (release, res.status_code))
        except:
            print("EXCEPTION: failed to download %s mirror list" % release)

def debian_crawler(root_path):
    debianReleases = ["bullseye", "buster", "jessie", "stretch", "wheezy"]
    OVALTemplate   = "https://www.debian.org/security/oval/oval-definitions-%s.xml"

    sourcesURL = "https://ftp.debian.org/debian/dists/%s/%s/source/Sources.gz"
    sourceRepos = ["main", "contrib", "non-free"]

    target_dirpath = os.path.join(root_path, "debian")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    for release in debianReleases:
        xml_url = OVALTemplate % release
        try:
            res = requests.get(xml_url)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "oval-definitions-%s.xml" % release), "wb") as f:
                    f.write(res.content)
            else:
                print("ERROR: failed to download %s, status code: %d" % (xml_url, res.status_code))
        except:
            print("EXCEPTION: failed to download %s" % xml_url)
        
        if release == "wheezy":
            pass
        else:
            try:
                for repo in sourceRepos:
                    src_dirpath = os.path.join(root_path, "debian", "dists", release, repo, "source")
                    if not os.path.exists(src_dirpath):
                        os.makedirs(src_dirpath)
                    gz_url = sourcesURL % (release, repo)
                    res = requests.get(gz_url)
                    if res.status_code == 200:
                        with open(os.path.join(src_dirpath, "Sources.gz"), "wb") as f:
                            f.write(res.content)
                    else:
                        print("ERROR: failed to download %s, status code: %d" % (gz_url, res.status_code))
            except:
                print("EXCEPTION: failed to download %s" % gz_url)

def oracle_crawler(root_path):
    allDB   = "https://linux.oracle.com/security/oval/com.oracle.elsa-all.xml.bz2"
    baseURL = "https://linux.oracle.com/security/oval/com.oracle.elsa-%d.xml.bz2"

    target_dirpath = os.path.join(root_path, "oracle")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    try:
        res = requests.get(allDB)
        if res.status_code == 200:
            with open(os.path.join(target_dirpath, "com.oracle.elsa-all.xml.bz2"), "wb") as f:
                f.write(res.content)
        else:
            print("ERROR: failed to download %s, status code: %d" % (allDB, res.status_code))
    except:
        print("EXCEPTION: failed to download %s" % allDB)

    for year in range(2007, datetime.datetime.now().year+1):
        bz_url = baseURL % year
        try:
            res = requests.get(bz_url)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "com.oracle.elsa-%d.xml.bz2" % year), "wb") as f:
                    f.write(res.content)
            else:
                print("ERROR: failed to download %s, status code: %d" % (bz_url, res.status_code))
        except:
            print("EXCEPTION: failed to download %s" % bz_url)

def photon_crawler(root_path):
    photonReleases = ["photon1", "photon2", "photon3", "photon4"]
    xml_url_base = "https://packages.vmware.com/photon/photon_oval_definitions/com.vmware.phsa-%s.xml"
    gz_url_base = "https://packages.vmware.com/photon/photon_oval_definitions/com.vmware.phsa-%s.xml.gz"

    target_dirpath = os.path.join(root_path, "photon")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    for release in photonReleases:
        try:
            res = requests.get(xml_url_base % release)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "com.vmware.phsa-%s.xml" % release), "wb") as f:
                    f.write(res.content)
            else:
                print("ERROR: failed to download %s xml file, status code: %d" % (release, res.status_code))
        except:
            print("EXCEPTION: failed to download %s xml file" % release)
        
        try:
            res= requests.get(gz_url_base % release)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "com.vmware.phsa-%s.xml.gz" % release), "wb") as f:
                    f.write(res.content)
            else:
                print("ERROR: failed to download %s xml.gz file, status code: %d" % (release, res.status_code))
        except:
            print("EXCEPTION: failed to download %s xml.gz file" % release)

def pyupio_crawler(root_path): # not available due to GFW
    defaultURL = "https://github.com/pyupio/safety-db/archive/master.tar.gz"

    target_dirpath = os.path.join(root_path, "pyupio")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    try:
        res = requests.get(defaultURL)
        if res.status_code == 200:
            with open(os.path.join(target_dirpath, "safety-db-master.tar.gz"), "wb") as f:
                f.write(res.content)
        else:
            print("ERROR: failed to download %s, status code: %d" % (defaultURL, res.status_code))
    except:
        print("EXCEPTION: failed to download %s" % defaultURL)

def rhel_crawler(root_path):
    target_dirpath = os.path.join(root_path, "redhat")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)
    
    # default oval
    rhelReleases = [6, 7, 8]
    dbURL = "https://access.redhat.com/security/data/oval/com.redhat.rhsa-RHEL%d.xml"

    for release in rhelReleases:
        try:
            res = requests.get(dbURL % release)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "com.redhat.rhsa-RHEL%d.xml" % release), "wb") as f:
                    f.write(res.content)
            else:
                print("ERROR: failed to download com.redhat.rhsa-RHEL%d.xml, status code: %d" % (release, res.status_code))
        except:
            print("EXCEPTION: failed to download com.redhat.rhsa-RHEL%d.xml" % release)

    # oval v2
    DefaultURL = "https://access.redhat.com/security/data/oval/v2/%s/%s"
    DefaultManifest = "https://access.redhat.com/security/data/oval/v2/PULP_MANIFEST"

    try:
        res = requests.get(DefaultManifest)
        if res.status_code == 200:
            with open(os.path.join(target_dirpath, "PULP_MANIFEST"), "wb") as f:
                f.write(res.content)

            exist_sub_dirs = []
            download_list = res.text.split("\n")

            for item in download_list:
                sub_dirname = item.split("/")[0]
                sub_dirpath = os.path.join(target_dirpath, sub_dirname)

                if sub_dirpath not in exist_sub_dirs:
                    if not os.path.exists(sub_dirpath):
                        os.makedirs(sub_dirpath)
                        exist_sub_dirs.append(sub_dirpath)
                
                filename = item.split("/")[1].split(",")[0]

                try:
                    res = requests.get(DefaultURL % (sub_dirname, filename))
                    if res.status_code == 200:
                        with open(os.path.join(sub_dirpath, filename), "wb") as f:
                            f.write(res.content)
                    else:
                        print("ERROR: failed to download %s/%s, status code: %d" % (sub_dirname, filename, res.status_code))
                except:
                    print("EXCEPTION: failed to download %s/%s" % (sub_dirname, filename))
        else:
            print("ERROR: failed to download %s, status code: %d" % (DefaultManifest, res.status_code))
    except:
        print("EXCEPTION: failed to download %s" % DefaultManifest)

def suse_crawler(root_path): # may not be available for opensuse.leap.42.3
    suseReleases = [
        "suse.linux.enterprise.server.15",
        "suse.linux.enterprise.server.12",
        "suse.linux.enterprise.server.11",
        "opensuse.leap.15.1",
        "opensuse.leap.15.0",
        "opensuse.leap.42.3"
    ]

    baseURL = "https://support.novell.com/security/oval/%s.xml"
    bakURL = "https://ftp.suse.com/pub/projects/security/oval/%s.xml"

    target_dirpath = os.path.join(root_path, "suse")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    for release in suseReleases:
        try:
            res = requests.get(baseURL % release)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "%s.xml" % release), "wb") as f:
                    f.write(res.content)
            elif res.status_code == 403:
                print("Default URL is Access Forbidden, trying backup ftp server")
                try:
                    res = requests.get(bakURL % release)
                    if res.status_code == 200:
                        with open(os.path.join(target_dirpath, "%s.xml" % release), "wb") as f:
                            f.write(res.content)
                    else:
                        print("ERROR: failed to download %s.xml from backup ftp server, status code: %d" % (release, res.status_code))
                except:
                    print("EXCEPTION: failed to download %s.xml from backup ftp server" % release)
        except:
            print("EXCEPTION: failed to download %s.xml" % release)

def ubuntu_crawler(root_path):
    ubuntuMatrix = { # shouldBzipFetch
        "artful":  False,
        "bionic":  True,
        "cosmic":  True,
        "disco":   True,
        "precise": False,
        "trusty":  True,
        "xenial":  True,
        "eoan":    True,
        "focal":   True,
        "impish":  True,
    }

    OVALTemplateBzip = "https://people.canonical.com/~ubuntu-security/oval/com.ubuntu.%s.cve.oval.xml.bz2"
    OVALTemplate     = "https://people.canonical.com/~ubuntu-security/oval/com.ubuntu.%s.cve.oval.xml"

    target_dirpath = os.path.join(root_path, "ubuntu")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    for release in ubuntuMatrix.keys():
        if ubuntuMatrix[release]:
            try:
                res = requests.get(OVALTemplateBzip % release)
                if res.status_code == 200:
                    with open(os.path.join(target_dirpath, "com.ubuntu.%s.cve.oval.xml.bz2" % release), "wb") as f:
                        f.write(res.content)
                else:
                    print("ERROR: failed to download %s xml.bz2 file, status code: %d" % (release, res.status_code))
            except:
                print("EXCEPTION: failed to download %s xml.bz2 file" % release)
        else:
            try:
                res = requests.get(OVALTemplate % release)
                if res.status_code == 200:
                    with open(os.path.join(target_dirpath, "com.ubuntu.%s.cve.oval.xml" % release), "wb") as f:
                        f.write(res.content)
                else:
                    print("ERROR: failed to download %s xml file, status code: %d" % (release, res.status_code))
            except:
                print("EXCEPTION: failed to download %s xml file" % release)

def cvss_crawler(root_path):
    DefaultFeeds = "https://nvd.nist.gov/feeds/json/cve/1.1/"

    target_dirpath = os.path.join(root_path, "cvss")
    if not os.path.exists(target_dirpath):
        os.makedirs(target_dirpath)

    for year in range(2002, datetime.datetime.now().year+1):
        metafileURL = DefaultFeeds + "nvdcve-1.1-%d.meta" % year
        gzURL = DefaultFeeds + "nvdcve-1.1-%d.json.gz" % year
        try:
            res = requests.get(metafileURL)
            if res.status_code == 200:
                with open(os.path.join(target_dirpath, "nvdcve-1.1-%d.meta" % year), "wb") as f:
                    f.write(res.content)
                try:
                    res = requests.get(gzURL)
                    if res.status_code == 200:
                        with open(os.path.join(target_dirpath, "nvdcve-1.1-%d.json.gz" % year), "wb") as f:
                            f.write(res.content)
                    else:
                        print("ERROR: failed to download %s, status code: %d" % (gzURL, res.status_code))
                except:
                    print("EXCEPTION: failed to download %s" % gzURL)
            else:
                print("ERROR: failed to download %s, status code: %d" % (metafileURL, res.status_code))
        except:
            print("EXCEPTION: failed to download %s" % metafileURL)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog='PROG', description='Generate alpine/amazon/debian/oracle/photon/pyupio/rhel/suse/ubuntu/cvss vuln database.')
    arg_parser.add_argument('-o', metavar='<DATABASE DIR>', required=True, help='Specify the directory to store vuln database. (e.g. /home/user/secdb/)')
    args = arg_parser.parse_args()
    root_path = args.o
    
    alpine_crawler(root_path)
    amazon_crawler(root_path)
    debian_crawler(root_path)
    oracle_crawler(root_path)
    photon_crawler(root_path)
    pyupio_crawler(root_path)
    rhel_crawler(root_path)
    suse_crawler(root_path)
    ubuntu_crawler(root_path)
    cvss_crawler(root_path)
    