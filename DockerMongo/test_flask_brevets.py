import unittest
import sys
sys.argv = [sys.argv[0]]
import flask_brevets


class TestBrevets(unittest.TestCase):
    
    def setUp(self):
        self.app = flask_brevets.app.test_client()
        flask_brevets.db.times.delete_many({})
    
    def test_submit(self):
        controls = [{"km": "10", "open": "Sun 1/1 0:18", "close": "Sun 1/1 1:30"}]
        response = self.app.post("/insert", json=controls)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        stored = list(flask_brevets.db.times.find({}, {"_id": 0}))
        self.assertEqual(stored, controls)

    def test_display(self):
        controls = [{"km": "10", "open": "Sun 1/1 0:18", "close": "Sun 1/1 1:30"}]
        flask_brevets.db.times.insert_many([dict(controls[0])])
        response = self.app.get("/fetch")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["times"], controls)

if __name__ == "__main__":
    unittest.main()