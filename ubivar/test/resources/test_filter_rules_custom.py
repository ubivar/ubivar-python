import os
import ubivar
import warnings
from ubivar.test.helper import (UbivarTestCase, NOW)


DUMMY_RULES_CUSTOM = {
        "description": "DUMMY RULES_CUSTOM",
        "feature": "email_domain",
        "is_active": "true",
        "value": "gmail.com"
        }


class UbivarAPIResourcesTests(UbivarTestCase):

    def test_filter_rules_custom_create(self):
        response = ubivar.FilterRulesCustom.create(**DUMMY_RULES_CUSTOM)
        filterRulesCustom = response.data[len(response.data)-1]
        self.assertTrue(hasattr(response, "data"))
        self.assertEqual(filterRulesCustom["description"], DUMMY_RULES_CUSTOM["description"])
        self.assertEqual(filterRulesCustom["feature"]    , DUMMY_RULES_CUSTOM["feature"])
        self.assertEqual(filterRulesCustom["value"]      , DUMMY_RULES_CUSTOM["value"])
        self.assertEqual(filterRulesCustom["is_active"]  , DUMMY_RULES_CUSTOM["is_active"])
        self.assertEqual(response.object, "filter_rules_custom")

    def test_filter_rules_custom_list(self):
        response = ubivar.FilterRulesCustom.list()
        self.assertTrue(hasattr(response.data, "__iter__"))
        self.assertTrue(response.object == "filter_rules_custom")

    def test_filter_rules_custom_update(self):
        response = ubivar.FilterRulesCustom.list()
        for i in range(0, len(response.data)):
            response = ubivar.FilterRulesCustom.delete(str(i))
        response = ubivar.FilterRulesCustom.create(**DUMMY_RULES_CUSTOM)
        response = ubivar.FilterRulesCustom.create(**DUMMY_RULES_CUSTOM)

        newDescription = "new description"
        newValue = "new value"
        newStatus= "false"
        newFeature = "new feature"
        response = ubivar.FilterRulesCustom.update("1", description=newDescription, 
                                                 value=newValue, is_active=newStatus,
                                                 feature=newFeature)
        filterRulesCustom = response.data[len(response.data) - 1]
        self.assertEqual(filterRulesCustom["description"], newDescription)
        self.assertEqual(filterRulesCustom["value"], newValue)
        self.assertEqual(filterRulesCustom["is_active"], newStatus)
        self.assertEqual(filterRulesCustom["feature"], newFeature)
        self.assertEqual(response.object, "filter_rules_custom")

    def test_filter_rules_custom_delete(self):
        response = ubivar.FilterRulesCustom.list()
        for i in range(0, len(response.data)):
            response = ubivar.FilterRulesCustom.delete(str(i))
            self.assertEqual(response.object, "filter_rules_custom")
