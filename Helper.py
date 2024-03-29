import inspect
import appdaemon.plugins.hass.hassapi as hass
import re
import sys


class BaseClass(hass.Hass):

    def _log(self, msg):
        if "appdaemontestframework" in sys.modules:
            print(msg)
        else:
            self.log(msg)

    def _init_filter(self):
        self._filter_blacklist = None
        if self.args.get("filter_blacklist", None) is not None and self.args.get("filter_blacklist")!="":
            self._filter_blacklist=self.args.get("filter_blacklist")
        self._log_debug(self._filter_blacklist)
        self._log_debug(f"filter_blacklist: {self._filter_blacklist}")

        self._filter_whitelist = None
        if self.args.get("filter_whitelist", None) is not None and self.args.get("filter_whitelist")!="":
            self._filter_whitelist=self.args.get("filter_whitelist")
        self._log_debug(f"filter_whitelist: {self._filter_whitelist}")

    def _log_info(self, msg, prefix=None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        if prefix is not None and prefix != "":
            self._log("%s: %s: %s: %s" %
                     (self.__class__.__name__, prefix, callername, msg))
        else:
            self._log("%s: %s: %s" % (self.__class__.__name__, callername, msg))

    def _log_debug(self, msg, prefix=None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        if self.args["debug"]:
            if prefix is not None and prefix != "":
                self._log("DEBUG: %s: %s: %s: %s" %
                         (self.__class__.__name__, prefix, callername, msg))
            else:
                self._log("DEBUG: %s: %s: %s" %
                         (self.__class__.__name__, callername, msg))

    def _log_error(self, msg, prefix=None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        if prefix is not None and prefix != "":
            self._log("ERROR: %s: %s: %s: %s" %
                     (self.__class__.__name__, prefix, callername, msg))
        else:
            self._log("ERROR: %s: %s: %s" % (self.__class__.__name__, callername, msg))

    def _getattribute(self, statedict, entity, atr):
        return statedict.get(entity).get("attributes").get(atr, None)

    def _convertname(self, name):
        if name is not None and name != "":
            return name.lower().replace(" ", "_")
        else:
            return None

    def _getid(self, statedict, entity):
        idlist = ['friendly_name', 'id', 'value_id']
        count = 0
        id = None
        while id is None and count < len(idlist):
            self._log_debug("idlist: %s" % idlist[count])
            id = self._convertname(self._getattribute(
                statedict, entity, idlist[count]))
            count += 1
        if id is None:
            # id is still None. We have to clarify where to get the id
            self._log_debug("Could not detect id of the item. Values %s" %
                            self.get_state(entity, attribute="all"))
        return id

    def _anyone_home(self, regex='^person.*'):
        statedict = self.get_state()
        anyonehome = False
        for entity in statedict:
            if re.match(regex, entity, re.IGNORECASE):
                id = self._getid(statedict, entity)
                state = self.get_state(entity)
                self._log_debug("Person %s is %s" % (id, state))
                if state == "home":
                    anyonehome = True
        return anyonehome

    def import_install_module(self, package):
        import subprocess
        import sys
        import importlib
        importedmodule = None
        try:
            importedmodule = importlib.import_module(package)
        except ImportError:
            self._log_debug(sys.executable)
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except Exception as e:
                self._log_error(e)
        finally:
            importedmodule = importlib.import_module(package)
        return importedmodule

    def _get_state_filtered(self):
        statedict = self.get_state()
        filtered_statedict=dict()
        for entity in statedict:
            self._log_debug(f"enitiy: {entity}")
            #filter by blacklist
            if self._filter_blacklist is not None:
                prepare="|".join(self._filter_blacklist)
                blacklistregex=f"({prepare})"
            else:
                blacklistregex=None

            #filter by whitelist
            if self._filter_whitelist is not None:
                prepare="|".join(self._filter_whitelist)
                whitelistregex=f"({prepare})"
            else:
                whitelistregex=".*"

            #apply filter
            matchedblacklist=False
            if blacklistregex is not None and re.search(blacklistregex, entity, re.IGNORECASE):
                matchedblacklist=True
            matchedwhitelist=False
            if re.search(whitelistregex, entity, re.IGNORECASE):
                matchedwhitelist=True
            self._log_debug(f"Matched Blacklist: {matchedblacklist}")
            self._log_debug(f"Matched Whitelist: {matchedwhitelist}")
            if not matchedblacklist and matchedwhitelist:
                self._log_debug(f"Add entity {entity} to filtered_statedict")
                filtered_statedict.update({entity: statedict.get(entity)})

        return filtered_statedict

