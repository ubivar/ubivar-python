import os
import oriskami
import warnings
from oriskami.test.helper import (OriskamiTestCase, NOW)


DUMMY_WHITELIST = {
        "description": "DUMMY WHITELIST",
        "feature": "email_domain",
        "is_active": "true",
        "value": "gmail.com"
        }


class OriskamiAPIResourcesTests(OriskamiTestCase):

    def test_filter_whitelist_create(self):
        response = oriskami.FilterWhitelist.create(**DUMMY_WHITELIST)
        filterWhitelist = response.data[len(response.data)-1]
        self.assertTrue(hasattr(response, "data"))
        self.assertEqual(filterWhitelist["description"], DUMMY_WHITELIST["description"])
        self.assertEqual(filterWhitelist["feature"], DUMMY_WHITELIST["feature"])
        self.assertEqual(filterWhitelist["value"], DUMMY_WHITELIST["value"])
        self.assertEqual(filterWhitelist["is_active"], DUMMY_WHITELIST["is_active"])
        self.assertEqual(response.object, "filter_whitelists")

    def test_filter_whitelist_list(self):
        response = oriskami.FilterWhitelist.list()
        self.assertTrue(hasattr(response.data, "__iter__"))
        self.assertTrue(response.object == "filter_whitelists")

    def test_filter_whitelist_update(self):
        response = oriskami.FilterWhitelist.list()
        for i in range(0, len(response.data)):
            response = oriskami.FilterWhitelist.delete(str(i))
        response = oriskami.FilterWhitelist.create(**DUMMY_WHITELIST)
        response = oriskami.FilterWhitelist.create(**DUMMY_WHITELIST)

        newDescription = "new description"
        newValue = "new value"
        newStatus= "false"
        newFeature = "new feature"
        response = oriskami.FilterWhitelist.update("1", description=newDescription, 
                                                 value=newValue, is_active=newStatus,
                                                 feature=newFeature)
        filterWhitelist = response.data[1]
        self.assertEqual(filterWhitelist["description"], newDescription)
        self.assertEqual(filterWhitelist["value"], newValue)
        self.assertEqual(filterWhitelist["is_active"], newStatus)
        self.assertEqual(filterWhitelist["feature"], newFeature)
        self.assertEqual(response.object, "filter_whitelists")

    def test_filter_whitelist_delete(self):
        response = oriskami.FilterWhitelist.list()
        for i in range(0, len(response.data)):
            response = oriskami.FilterWhitelist.delete(str(i))
            self.assertEqual(response.object, "filter_whitelists")
