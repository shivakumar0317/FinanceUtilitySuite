import unittest

from desktop.reports.report_registry import (
    DEFAULT_REPORTS,
    ReportDefinition,
    ReportRegistry,
    get_report_registry,
)


class ReportRegistryTests(unittest.TestCase):
    def test_default_registry_contains_expected_reports(self):
        registry = get_report_registry()
        self.assertEqual(len(registry), 5)
        self.assertEqual(registry.get("portfolio").title, "Portfolio Report")
        self.assertEqual(registry.get("analytics").title, "Analytics Report")
        self.assertEqual(registry.get("client_holdings").title, "Client Holdings Report")

    def test_available_excludes_coming_soon(self):
        registry = ReportRegistry(DEFAULT_REPORTS)
        self.assertEqual([r.report_id for r in registry.available()], [
            "portfolio", "analytics", "client_holdings"
        ])

    def test_duplicate_registration_is_rejected(self):
        report = ReportDefinition("sample", "Sample", "📄", "Sample report")
        registry = ReportRegistry([report])
        with self.assertRaises(ValueError):
            registry.register(report)

    def test_replace_registration(self):
        original = ReportDefinition("sample", "Sample", "📄", "Original")
        replacement = ReportDefinition("sample", "Updated", "📊", "Replacement")
        registry = ReportRegistry([original])
        registry.register(replacement, replace=True)
        self.assertEqual(registry.get("sample"), replacement)

    def test_search_matches_title_description_and_category(self):
        registry = ReportRegistry(DEFAULT_REPORTS)
        self.assertEqual([r.report_id for r in registry.search("analytics")], ["analytics", "risk_analytics"])
        self.assertEqual([r.report_id for r in registry.search("client")], ["client_holdings"])
        self.assertEqual([r.report_id for r in registry.search("risk")], ["mtf_risk", "risk_analytics"])

    def test_invalid_definition_is_rejected(self):
        with self.assertRaises(ValueError):
            ReportDefinition("", "Title", "📄", "Description")
        with self.assertRaises(ValueError):
            ReportDefinition("bad id!", "Title", "📄", "Description")
        with self.assertRaises(ValueError):
            ReportDefinition("valid", "Title", "📄", "Description", status="hidden")

    def test_unregister(self):
        registry = ReportRegistry(DEFAULT_REPORTS)
        self.assertTrue(registry.unregister("portfolio"))
        self.assertFalse(registry.unregister("portfolio"))
        with self.assertRaises(KeyError):
            registry.get("portfolio")


if __name__ == "__main__":
    unittest.main()
