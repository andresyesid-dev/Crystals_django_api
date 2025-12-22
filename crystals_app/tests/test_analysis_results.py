from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch
from crystals_app.models import AnalysisResults
from crystals_app.views.analysisresults_view import add_analysis_results
import json

class AnalysisResultsTestCase(TestCase):
    def test_add_analysis_results(self):
        factory = RequestFactory()
        
        data = {
            "mean": 10.5,
            "cv": 5.2,
            "pct_fine": 1.1,
            "pct_small": 2.2,
            "pct_optimal": 3.3,
            "pct_large": 4.4,
            "pct_very_large": 5.5,
            "ratio_l_to_w": 0.8,
            "elongated_crystals": 15.0,
            "pct_powder": 0.5,
            "historic_report_id": 123
        }
        
        request = factory.post(
            '/analysis-results/add',
            data=json.dumps(data),
            content_type='application/json'
        )
        request.META['HTTP_X_FACTORY_ID'] = 1  # Use a valid factory ID

        # Patch JWTAuthentication to bypass auth check
        with patch('crystals_app.decorators.JWTAuthentication') as MockJWTAuth:
            mock_auth_instance = MockJWTAuth.return_value
            mock_user = MagicMock()
            mock_user.is_authenticated = True
            mock_user.username = 'testuser'
            mock_auth_instance.authenticate.return_value = (mock_user, 'fake_token')
            
            response = add_analysis_results(request)
            
            self.assertEqual(response.status_code, 200)
            
            resp_data = json.loads(response.content)
            self.assertTrue(resp_data.get("ok"))
            new_id = resp_data.get("id")
            self.assertIsNotNone(new_id)
            
            # Verify in DB
            obj = AnalysisResults.objects.get(id=new_id)
            self.assertEqual(obj.mean, 10.5)
            self.assertEqual(obj.historic_report_id, 123)
            self.assertEqual(obj.factory_id, 1)
