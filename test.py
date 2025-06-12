import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('text/html', response.content_type)

        self.assertTrue(len(response.data) > 0)

    def test_predict_crime_all(self):
    
        response = self.app.post('/predict_crime', data={
            'model': 'B',  
            'crime_type': 'ALL',
            'selected_state_ut': 'KERALA',  
            'districts': 'ALAPUZHA',  
            'YEAR': '2023'  
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.data.decode('utf-8') 
        expected_content = f'Predictions for All Target Crimes in ' 
        self.assertIn(expected_content, response_data)
       
        


    def test_predict_crime_single(self):
        
        response = self.app.post('/predict_crime', data={
            'model': 'B',  
            'crime_type': 'BURGLARY',  
            'selected_state_ut': 'KERALA',  
            'districts': 'ALAPUZHA',  
            'YEAR': '2023'  
        })

        self.assertEqual(response.status_code, 200)
        response_data = response.data.decode('utf-8')  
        expected_content = f'CRIME RATE FOR BURGLARY in ' 
        self.assertIn(expected_content, response_data)
       
if __name__ == '__main__':
    unittest.main()
