import requests
import unittest
import json
import os
from datetime import datetime

class YorubaCulturalAppTests(unittest.TestCase):
    def setUp(self):
        # Get the backend URL from the frontend .env file
        self.base_url = "https://021285e0-3d49-4149-8d95-676d24c64a6a.preview.emergentagent.com/api"
        self.session = requests.Session()
        print(f"\nTesting against API: {self.base_url}")

    def test_01_get_all_orisha(self):
        """Test GET /api/orisha - Should return 8 Òrìṣà profiles"""
        print("\n🔍 Testing GET /api/orisha - Should return 8 Òrìṣà profiles")
        
        response = self.session.get(f"{self.base_url}/orisha")
        
        # Check status code
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse response
        data = response.json()
        
        # Check that we have 8 Òrìṣà profiles
        self.assertEqual(len(data), 8, f"Expected 8 Òrìṣà profiles, got {len(data)}")
        
        # Check that each profile has the required fields
        required_fields = ["id", "name", "yoruba_name", "domains", "colors", "symbols", 
                          "sacred_number", "story", "yoruba_story", "diaspora", "constellation_position"]
        
        for orisha in data:
            for field in required_fields:
                self.assertIn(field, orisha, f"Field '{field}' missing from Òrìṣà profile")
        
        print(f"✅ Successfully retrieved {len(data)} Òrìṣà profiles")
        return data

    def test_02_get_specific_orisha(self):
        """Test GET /api/orisha/obatala - Should return Ọbàtálá profile"""
        print("\n🔍 Testing GET /api/orisha/obatala - Should return Ọbàtálá profile")
        
        response = self.session.get(f"{self.base_url}/orisha/obatala")
        
        # Check status code
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse response
        data = response.json()
        
        # Check that we have the correct Òrìṣà
        self.assertEqual(data["id"], "obatala", "Expected Òrìṣà ID to be 'obatala'")
        self.assertEqual(data["name"], "Ọbàtálá", "Expected Òrìṣà name to be 'Ọbàtálá'")
        
        # Check for specific attributes of Obatala
        self.assertIn("Creation", data["domains"], "Expected 'Creation' in Obatala's domains")
        self.assertIn("White", data["colors"], "Expected 'White' in Obatala's colors")
        
        print(f"✅ Successfully retrieved Ọbàtálá profile")
        return data

    def test_03_nonexistent_orisha(self):
        """Test GET /api/orisha/nonexistent - Should return 404"""
        print("\n🔍 Testing GET /api/orisha/nonexistent - Should return 404")
        
        response = self.session.get(f"{self.base_url}/orisha/nonexistent")
        
        # Check status code
        self.assertEqual(response.status_code, 404, f"Expected status code 404, got {response.status_code}")
        
        print(f"✅ Correctly received 404 for nonexistent Òrìṣà")

    def test_04_translate_english_to_yoruba(self):
        """Test POST /api/translate - Test Gemini translation (English to Yoruba)"""
        print("\n🔍 Testing POST /api/translate - English to Yoruba translation")
        
        test_text = "The river flows with wisdom and beauty."
        payload = {
            "text": test_text,
            "target_language": "yoruba"
        }
        
        response = self.session.post(f"{self.base_url}/translate", json=payload)
        
        # Check status code
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse response
        data = response.json()
        
        # Check response structure
        self.assertIn("original_text", data, "Missing 'original_text' in response")
        self.assertIn("translated_text", data, "Missing 'translated_text' in response")
        self.assertIn("language", data, "Missing 'language' in response")
        
        # Check original text matches
        self.assertEqual(data["original_text"], test_text, "Original text doesn't match")
        
        # Check that translated text is not empty
        self.assertTrue(len(data["translated_text"]) > 0, "Translated text is empty")
        
        # Check language
        self.assertEqual(data["language"], "yoruba", "Language should be 'yoruba'")
        
        print(f"✅ Successfully translated text to Yoruba")
        print(f"   Original: {data['original_text']}")
        print(f"   Translated: {data['translated_text']}")
        return data

    def test_05_translate_yoruba_to_english(self):
        """Test POST /api/translate - Test Gemini translation (Yoruba to English)"""
        print("\n🔍 Testing POST /api/translate - Yoruba to English translation")
        
        test_text = "Omi ṣàn pẹ̀lú ọgbọ́n àti ẹwà."
        payload = {
            "text": test_text,
            "target_language": "english"
        }
        
        response = self.session.post(f"{self.base_url}/translate", json=payload)
        
        # Check status code
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse response
        data = response.json()
        
        # Check response structure
        self.assertIn("original_text", data, "Missing 'original_text' in response")
        self.assertIn("translated_text", data, "Missing 'translated_text' in response")
        self.assertIn("language", data, "Missing 'language' in response")
        
        # Check original text matches
        self.assertEqual(data["original_text"], test_text, "Original text doesn't match")
        
        # Check that translated text is not empty
        self.assertTrue(len(data["translated_text"]) > 0, "Translated text is empty")
        
        # Check language
        self.assertEqual(data["language"], "english", "Language should be 'english'")
        
        print(f"✅ Successfully translated text to English")
        print(f"   Original: {data['original_text']}")
        print(f"   Translated: {data['translated_text']}")
        return data

    def test_06_get_daily_proverb(self):
        """Test GET /api/proverbs/daily - Should return daily proverb from Gemini"""
        print("\n🔍 Testing GET /api/proverbs/daily - Should return daily proverb")
        
        response = self.session.get(f"{self.base_url}/proverbs/daily")
        
        # Check status code
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse response
        data = response.json()
        
        # Check response structure
        self.assertIn("proverb", data, "Missing 'proverb' in response")
        self.assertIn("date", data, "Missing 'date' in response")
        
        # Check that proverb is not empty
        self.assertTrue(data["proverb"], "Proverb is empty")
        
        # Check date format
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            self.fail(f"Date format is incorrect: {data['date']}")
        
        print(f"✅ Successfully retrieved daily proverb")
        
        # Print proverb details
        if isinstance(data["proverb"], dict) and "yoruba" in data["proverb"]:
            print(f"   Yoruba: {data['proverb']['yoruba']}")
            print(f"   Translation: {data['proverb']['literal_translation']}")
        else:
            print(f"   Proverb: {data['proverb']}")
        
        return data

    def test_07_cultural_content_generation(self):
        """Test POST /api/cultural-content - Test Gemini cultural content generation"""
        print("\n🔍 Testing POST /api/cultural-content - Cultural content generation")
        
        payload = {
            "orisha_name": "Ṣàngó",
            "content_type": "story"
        }
        
        response = self.session.post(f"{self.base_url}/cultural-content", json=payload)
        
        # Check status code
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        
        # Parse response
        data = response.json()
        
        # Check response structure
        self.assertIn("orisha_name", data, "Missing 'orisha_name' in response")
        self.assertIn("content_type", data, "Missing 'content_type' in response")
        self.assertIn("content", data, "Missing 'content' in response")
        self.assertIn("generated_at", data, "Missing 'generated_at' in response")
        
        # Check content matches request
        self.assertEqual(data["orisha_name"], payload["orisha_name"], "Orisha name doesn't match")
        self.assertEqual(data["content_type"], payload["content_type"], "Content type doesn't match")
        
        # Check that content is not empty
        self.assertTrue(len(data["content"]) > 0, "Generated content is empty")
        
        print(f"✅ Successfully generated cultural content for {payload['orisha_name']}")
        print(f"   Content type: {data['content_type']}")
        print(f"   Content length: {len(data['content'])} characters")
        
        return data

def run_tests():
    suite = unittest.TestSuite()
    suite.addTest(YorubaCulturalAppTests('test_01_get_all_orisha'))
    suite.addTest(YorubaCulturalAppTests('test_02_get_specific_orisha'))
    suite.addTest(YorubaCulturalAppTests('test_03_nonexistent_orisha'))
    suite.addTest(YorubaCulturalAppTests('test_04_translate_english_to_yoruba'))
    suite.addTest(YorubaCulturalAppTests('test_05_translate_yoruba_to_english'))
    suite.addTest(YorubaCulturalAppTests('test_06_get_daily_proverb'))
    suite.addTest(YorubaCulturalAppTests('test_07_cultural_content_generation'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == "__main__":
    print("=" * 80)
    print("YORUBA CULTURAL APP API TESTS")
    print("=" * 80)
    result = run_tests()
    
    print("\n" + "=" * 80)
    print(f"TESTS SUMMARY: {result.testsRun} tests run")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("=" * 80)
    
    # Exit with appropriate code
    import sys
    sys.exit(len(result.failures) + len(result.errors))