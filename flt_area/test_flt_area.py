import unittest
import imp
import argparse
import numpy


class TestFltArea(unittest.TestCase):

    def setUp(self):
        flt_area = imp.load_source('flt_area', './flt_area')
        self.args = argparse.Namespace(area_file_pattern=[
                        '../test_data/MethaneAIR21rf04.nc',
                        '../test_data/MethaneAIR21rf05.nc',
                        '../test_data/MethaneAIR21rf06.nc',
                        '../test_data/MethaneAIR21rf07.nc',
                        '../test_data/MethaneAIR21rf08.nc'])
        self.flt_area = flt_area.FltArea()
        self.flt_area.calc(self.args)

    def tearDown(self):
        pass

    def test_latlon_list(self):
        self.assertTrue(isinstance(self.flt_area.lat, list))
        self.assertTrue(isinstance(self.flt_area.lon, list))

    def test_latlon_notzero(self):
        self.assertTrue(abs(self.flt_area.lat_max) > 1)
        self.assertTrue(abs(self.flt_area.lat_min) > 1)
        self.assertTrue(abs(self.flt_area.lon_max) > 1)
        self.assertTrue(abs(self.flt_area.lon_min) > 1)

    def test_latlon_notequal(self):
        self.assertNotEqual(self.flt_area.lat_max, self.flt_area.lat_min)
        self.assertNotEqual(self.flt_area.lon_max, self.flt_area.lon_min)

    def test_latlon_order(self):
        self.assertGreater(self.flt_area.lat_max, self.flt_area.lat_min)
        self.assertGreater(self.flt_area.lon_max, self.flt_area.lon_min)

    def test_latlon_float(self):
        self.assertTrue(isinstance(self.flt_area.lat_max, numpy.float32))
        self.assertTrue(isinstance(self.flt_area.lat_min, numpy.float32))
        self.assertTrue(isinstance(self.flt_area.lon_max, numpy.float32))
        self.assertTrue(isinstance(self.flt_area.lon_min, numpy.float32))


if __name__ == '__main__':
    unittest.main()
