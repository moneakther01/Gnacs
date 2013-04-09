#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson"
__license__="Simplified BSD"
import sys
# ujson is 20% faster
import json as json_formatter
try:
    import ujson as json
except ImportError:
    try:
        import json
    except ImportError:
        import simplejson as json

gnipError = "GNIPERROR"
gnipRemove = "GNIPREMOVE"

class WPacsCSV(object):
    def __init__(self, delim, options_user, options_rules, options_lang, options_struct, options_pretty):
        self.delim = delim
        self.cnt = 0
        self.options_user = options_user
        self.options_rules = options_rules
        self.options_lang = options_lang
        self.options_struct = options_struct
        self.options_pretty = options_pretty

    def cleanField(self,f):
        return f.strip().replace("\n"," ").replace("\r"," ").replace(self.delim, " ")

    def buildListString(self,l):
        # unicode output of list (without u's)
        res = '['
        for r in l:
            res += "'" + r + "',"
        if res.endswith(','):
            res = res[:-1]
        res += ']'
        return res

    def asString(self,l):
        if l is not None:
            return self.delim.join(l)
        return None

    def splitId(self, x):
        tmp = x.split(":")
        if len(tmp) > 1:
            return tmp[-1]
        else:
            return x

    def procRecord(self,x):
        record = []
        try:
            d = json.loads(x.strip())
        except ValueError:
            sys.stderr.write("Invalid JSON record (%d) %s, skipping\n"%(self.cnt, x.strip()))
            return None 
        if self.options_pretty:
            print json_formatter.dumps(d, indent=3)
            return None 
        try:
            if "verb" in d:
                verb = d["verb"]
            else:
                msg = "Unidentified meta message"
                for mtype in ["error", "warning", "info"]:
                    if mtype in d:
                        if "message" in d[mtype]:
                            msg = d[mtype]["message"]
                        elif "message" in d:
                            msg = d["message"]
                        continue
                    mtype = "Unidentified"
                record.append(gnipRemove)
                record.append(mtype)
                record.append(msg)
                return self.asString(record)
            if verb == "delete":
                record.append(gnipRemove)
                record.append(verb)
                record.append(self.cleanField(d["object"]["id"]))
                return self.asString(record)
            #
            record.append(d["id"])
            record.append(d["postedTime"])
            obj = d["object"]
            record.append(self.cleanField(obj["content"]))
            record.append(self.cleanField(obj["summary"]))
            #
            gnip = d["gnip"]
            actor = d["actor"]
            if self.options_lang:
                glang = "None"
                if "language" in gnip:
                    glang = gnip["language"]["value"]
                record.append(glang)
            if self.options_rules:
                rules = '[]'
                if "matching_rules" in gnip:
                    rules = self.buildListString([ "%s [%s]"%(l["value"], l["tag"]) for l in gnip["matching_rules"]])
                record.append(rules)
            if self.options_struct:
                target = d["target"]
                # site
                record.append(str(target["wpBlogId"]))
                # blog link
                record.append(str(target["link"]))
                # object
                record.append(str(obj["wpPostId"]))
                # link to post
                record.append(str(obj["link"]))
            if self.options_user:
                tmp = self.splitId(actor["id"])
                record.append(tmp)
            #
            self.cnt += 1
            return self.asString(record)
        except KeyError:
            sys.stderr.write("Field missing from record (%d), skipping\n"%self.cnt)
            record.append(gnipError)
            return self.asString(record)

