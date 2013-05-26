# -*- coding: utf-8 -*-

from ctypes import *
from ctypes import util

security = cdll.LoadLibrary(util.find_library("Security"))


class Keychain(object):
    def __init__(self, service):
        self.service = c_char_p(service)
        self.serviceLen = c_ulong(len(service))

    def storePassword(self, account, password):
        acctLen = c_ulong(len(account))
        pwLen = c_ulong(len(password))
        acctData = c_char_p(account)
        pwData = create_string_buffer(password)
        security.SecKeychainAddGenericPassword(
                    None,
                    self.serviceLen,
                    self.service,
                    acctLen,
                    acctData,
                    pwLen,
                    pwData,
                    None
            )

    def retrievePassword(self, account):
        acctLen = c_ulong(len(account))
        acctData = c_char_p(account)
        pwLen = pointer(c_ulong())
        pwData = pointer(c_char_p())

        security.SecKeychainFindGenericPassword(
                    None,
                    self.serviceLen,
                    self.service,
                    acctLen,
                    acctData,
                    pwLen,
                    pwData,
                    None
            )

        intendedLen = pwLen.contents.value
        if pwData.contents.value != None:
            return pwData.contents.value[0:intendedLen]
        else:
            return None

    def modifyPassword(self, account, newPassword):
        acctLen = c_ulong(len(account))
        newPwLen = c_ulong(len(newPassword))
        itemRef = pointer(c_void_p())
        newPwData = create_string_buffer(newPassword)

        security.SecKeychainFindGenericPassword(
                    None,
                    self.serviceLen,
                    self.service,
                    acctLen,
                    account,
                    None,
                    None,
                    itemRef
            )
        security.SecKeychainItemModifyAttributesAndData(
                itemRef.contents,
                None,
                newPwLen,
                newPwData
        )

    def deletePassword(self, account):
        acctLen = c_ulong(len(account) + 1)
        itemRef = c_void_p()
        security.SecKeychainFindGenericPassword(
                    None,
                    self.serviceLen,
                    self.service,
                    acctLen,
                    account,
                    None,
                    None,
                    byref(itemRef)
            )
        security.SecKeychainItemDelete(itemRef)
