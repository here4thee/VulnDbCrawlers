# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import xml.sax, json, jsonpath, argparse
from pathlib import Path
 
class VulnerabilityHandler( xml.sax.ContentHandler ):
    def __init__(self, nvd_json_filepath, database_filepath, split_number):
        self.count = 0
        self.vulns = []
        self.CurrentData = ""
        self.number = ""            # CNVD编号
        self.title = ""             # 漏洞名称
        self.serverity = ""         # 严重等级
        self.products = []          # 受影响软件
        self.isEvent = ""           # 漏洞类别
        self.submitTime = ""        # 提交时间
        self.openTime = ""          # 公开时间
        self.discovererName = ""    # 漏洞提交者
        self.referenceLink = ""     # 参考链接
        self.formalWay = ""         # 修补方案
        self.description = ""       # 漏洞描述
        self.patchName = ""         # 补丁名称
        self.patchDescription = ""  # 补丁描述
        self.cveNumber = ""         # CVE编号
        self.cveUrl = ""            # CVE链接
        self.nvd_json_filepath = nvd_json_filepath
        self.database_filepath = database_filepath
        self.split_number = split_number
 
    # 元素开始事件处理
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "vulnerability":
            self.products = []
 
    # 元素结束事件处理
    def endElement(self, tag):
        if tag == "vulnerability" and self.cveNumber:
            try:
                vulnyear = self.cveNumber.split("-")[1].strip()
                filepath = Path(str(self.nvd_json_filepath) % (vulnyear, self.cveNumber.strip()))
                severity = "" # NVD严重等级
                cpe23Uri = []
                
                if filepath.exists():
                    with open(filepath) as f:
                        jsondata = json.load(f)
                        if "baseMetricV3" in jsondata["impact"]:
                            severity = jsondata["impact"]["baseMetricV3"]["cvssV3"]["baseSeverity"]
                        elif "baseMetricV2" in jsondata["impact"]:
                            severity = jsondata["impact"]["baseMetricV2"]["severity"]
                        else:
                            severity = "None"
                        cpe23Uri = jsonpath.jsonpath(jsondata["configurations"], '$..cpe23Uri')
                    
                    if isinstance(cpe23Uri, list):
                        packages = []
                        systems = []
                        for acpe in cpe23Uri:
                            cpe_slices = acpe.split(":")
                            if cpe_slices[2] == "a":
                                pkg = {}
                                pkg["name"] = cpe_slices[4]
                                pkg["version"] = cpe_slices[5]
                                pkg["cpe"] = acpe
                                packages.append(pkg)
                            if cpe_slices[2] == "o":
                                sys = {}
                                sys["vendor"] = cpe_slices[3]
                                sys["product"] = cpe_slices[4]
                                sys["version"] = cpe_slices[5]
                                systems.append(sys)
                        
                        if len(packages) == 0:
                            pkg = {}
                            pkg["name"] = "Unknown"
                            pkg["version"] = "Unknown"
                            pkg["cpe"] = "Unknown"
                            packages.append(pkg)
                        if len(systems) == 0:
                            sys = {}
                            sys["vendor"] = "Unknown"
                            sys["product"] = "Unknown"
                            sys["version"] = "Unknown"
                            systems.append(sys)
                        
                        for pkg in packages:
                            for sys in systems:
                                vuln = {}
                                vuln["cnvdNumber"] = self.number.strip()
                                vuln["title"] = self.title.strip()
                                vuln["serverity"] = self.serverity.strip()
                                vuln["products"] = "  ".join(self.products)
                                vuln["vulnType"] = self.isEvent.strip()
                                vuln["submitTime"] = self.submitTime.strip()
                                vuln["openTime"] = self.openTime.strip()
                                vuln["discovererName"] = self.discovererName.strip()
                                vuln["referenceLink"] = self.referenceLink.strip()
                                vuln["formalWay"] = self.formalWay.strip()
                                vuln["description"] = self.description.strip()
                                vuln["patchName"] = self.patchName.strip()
                                vuln["patchDescription"] = self.patchDescription.strip()
                                vuln["cveNumber"] = self.cveNumber.strip()
                                vuln["cveUrl"] = self.cveUrl.strip()
                                vuln["nvdSeverity"] = severity.strip()
                                vuln["package"] = pkg
                                vuln["system"] = sys
                                self.vulns.append(vuln)
                                if len(self.vulns) >= self.split_number:
                                    output_filepath = Path(str(self.database_filepath) % self.count)
                                    with open(output_filepath, "w") as f:
                                        json.dump(self.vulns, f)
                                    self.count += 1
                                    self.vulns = []
            except:
                # print(self.cveNumber)
                pass
        self.CurrentData = ""
 
    # 内容事件处理
    def characters(self, content):
        if self.CurrentData == "number":
            self.number = content
        elif self.CurrentData == "title":
            self.title = content
        elif self.CurrentData == "serverity":
            self.serverity = content
        elif self.CurrentData == "product":
            self.products.append(xml.sax.saxutils.unescape(content))
        elif self.CurrentData == "isEvent":
            self.isEvent = content
        elif self.CurrentData == "submitTime":
            self.submitTime = content
        elif self.CurrentData == "openTime":
            self.openTime = content
        elif self.CurrentData == "discovererName":
            self.discovererName = content
        elif self.CurrentData == "referenceLink":
            self.referenceLink = content
        elif self.CurrentData == "formalWay":
            self.formalWay = content
        elif self.CurrentData == "description":
            self.description = content
        elif self.CurrentData == "patchName":
            self.patchName = content
        elif self.CurrentData == "patchDescription":
            self.patchDescription = content
        elif self.CurrentData == "cveNumber":
            self.cveNumber = content
        elif self.CurrentData == "cveUrl":
            self.cveUrl = content
  
if ( __name__ == "__main__"):
    arg_parser = argparse.ArgumentParser(prog='PROG', description='Generate CNVD vuln database.')
    arg_parser.add_argument('-c', metavar='<CNVD XML DIR>', required=True, help='Specify the directory including CNVD info. (e.g. /home/user/cnvd_xml_files/)')
    arg_parser.add_argument('-n', metavar='<NVD JSON DIR>', required=True, help='Specify the directory including NVD info. (e.g. /home/user/vuln-list-main/)')
    arg_parser.add_argument('-o', metavar='<DATABASE DIR>', required=True, help='Specify the directory to store CNVD database. (e.g. /home/user/secdb/cnvd/)')
    arg_parser.add_argument('-s', metavar='<SPLIT NUMBER>', type=int, default=40000, help='Number of vulnerabilities in a JSON file. (default. 40000)') # storage will be ~90 MB with 40k vulns in a JSON file
    args = arg_parser.parse_args()
    
    split_number = args.s
    cnvd_xml_dirpath = Path(args.c)
    nvd_json_filepath = Path(args.n).joinpath("nvd/%s/%s.json")
    database_filepath = Path(args.o).joinpath("cnvd-%04d.json")
    if not Path(args.o).exists():
        Path(args.o).mkdir(parents=True, exist_ok=True)

    # 创建一个 XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    
    # 重写 ContextHandler
    Handler = VulnerabilityHandler(nvd_json_filepath, database_filepath, split_number)
    parser.setContentHandler( Handler )

    for filepath in cnvd_xml_dirpath.glob('*.xml'):
        parser.parse(filepath)

'''
python3 cnvd_xml_handler.py -n ~/vuln-list-main -c ~/cnvd_xml_files -o ~/secdb/cnvd/ -s 40000
'''
