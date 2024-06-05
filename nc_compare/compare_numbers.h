// -*- C++ -*-
#ifndef _compare_numbers_h_
#define _compare_numbers_h_

#include <math.h>

/**
 * The compare_floating_point class parameterizes floating point comparison
 * methods and allows alternate methods to be configured and selected.  For
 * testing that floating point values are near each other, regardless of
 * magnitude, there are implementations for each of two diferent approaches.
 *
 * One approach is based on the number of distinct values between two numbers.
 * Closer values differ by fewer Units in the Last Places (bits).  The ULPs
 * can be computed by translating the IEEE bit representation into integers
 * whose difference is the number of representable floats between the two
 * numbers, as described here:
 *
 * http://www.cygnus-software.com/papers/comparingfloats/comparingfloats.htm
 *
 * However, that implementation is no longer used, because it lacks
 * portability and is harder to understand, and the original implementations
 * have been removed.  The current implementations, in
 * almost_equal_float_nsteps() and almost_equal_double_nsteps(), use the
 * nextafter() functions available as of C99.  The nextafter() functions allow
 * stepping through each successive representable floating point value.  If
 * two floats are not equal after stepping from one to the other for a maximum
 * number of steps, then they are not close enough.  The performance may not
 * be as good as using the integer representation, but so far that has not
 * been a concern.
 *
 * Since the _nsteps functions work by counting steps between two numbers, the
 * number of ULPs is translated to (1 << ulps) - 1 steps.  That is, 1 ULP bit
 * represents one step, since that changes the least significant bit.  2 ULP
 * bits is within 3 steps, ie, either the two numbers are exactly equal down
 * to the least significant bit, or they are only 3 steps away from each
 * other.  If the last two bits of A are 00, then the last two bits of B can
 * be 00, 01, 10, or 11.  The magnitude of those steps depends on the
 * exponent.
 *
 * The other floating point comparison approach is based strictly on the
 * magnitude of the difference between the two numbers.  Two numbers differ if
 * their absolute difference exceeds some delta.  Given the same delta, two
 * larger numbers must have fewer bit differences to compare as equal compared
 * to two smaller numbers.
 **/


/**
 * @brief Translate ULPs to steps.
 * 
 * One bit is one step, two bits are 3 steps, and so on.
 * 
 * @param nulps 
 * @return int 
 */

inline int ulps_to_steps(int nulps)
{
  return (1 << nulps) - 1;
}


/**
 * The nsteps comparison functions use the nextafter*() functions added to
 * C99.  Once C++11 is more widely available, these can switch to using the
 * overloaded nextafter() functions. @p nsteps must be >= 0.
 *
 **/
inline bool
almost_equal_float_nsteps(float a, float b, int nsteps)
{
  int i = 0;
  while (i++ <= nsteps)
  {
    if (a == b)
      return true;
    a = nextafterf(a, b);
  }
  return false;
}

inline bool
almost_equal_double_nsteps(double a, double b, int nsteps)
{
  int i = 0;
  while (i++ <= nsteps)
  {
    if (a == b)
      return true;
    a = nextafter(a, b);
  }
  return false;
}


/**
 * Parameterize floating point comparisons.  This class provides alternate
 * ways to test two floating point numbers for equality, testing either
 * that their difference is within an absolute delta or that they are equal
 * within some number of Units in the Last Place (ULPs).  These objects
 * can be copied and constructed in place, so it is convenient to construct
 * and configure a floating point comparison like so:
 *
 * compare_floating_point().setDelta(1e-8).useDelta().near_equal(x, y);
 *
 **/
class compare_floating_point
{
public:
  /**
   * Construct the default floating point comparison object.  Floating
   * point values are equal if within 2 steps of each other.
   **/
  compare_floating_point() :
    _fdelta(1e-6),
    _ddelta(1e-10),
    _nulps(4)
  {
    useULPS();
  }

  /**
   * This template method is just a convenient way to compare any numeric
   * types, where the default implementation tests for exact equality.  The
   * template is specialized below for the float and double types to use
   * the inexact comparisons.
   **/
  template <typename T>
  inline bool
  near_equal(const T& left, const T& right)
  {
    return left == right;
  }

  compare_floating_point&
  useDelta()
  {
    _float_equal = &compare_floating_point::near_equal_delta_float;
    _double_equal = &compare_floating_point::near_equal_delta_double;
    return *this;
  }

  compare_floating_point&
  useULPS()
  {
    _float_equal = &compare_floating_point::near_equal_ulps_float;
    _double_equal = &compare_floating_point::near_equal_ulps_double;
    return *this;
  }

  compare_floating_point&
  setDelta(double ddelta)
  {
    _ddelta = ddelta;
    _fdelta = ddelta;
    return *this;
  }

  compare_floating_point&
  setFloatDelta(float efloat)
  {
    _fdelta = efloat;
    return *this;
  }

  compare_floating_point&
  setDoubleDelta(double edouble)
  {
    _ddelta = edouble;
    return *this;
  }

  compare_floating_point&
  setULPS(int nulps)
  {
    _nulps = nulps;
    return *this;
  }

  int
  getULPS()
  {
    return _nulps;
  }

  compare_floating_point&
  setNansEqual(bool nans_equal)
  {
    _nans_equal = nans_equal;
    return *this;
  }

  bool
  getNansEqual()
  {
    return _nans_equal;
  }

  bool
  near_equal_ulps_float(float left, float right)
  {
    return almost_equal_float_nsteps(left, right, ulps_to_steps(_nulps));
  }

  bool
  near_equal_ulps_double(double left, double right)
  {
    return almost_equal_double_nsteps(left, right, ulps_to_steps(_nulps));
  }

  bool
  near_equal_delta_float(float left, float right)
  {
    return (left - right) < _fdelta && (left - right) > -_fdelta;
  }

  bool
  near_equal_delta_double(double left, double right)
  {
    return (left - right) < _ddelta && (left - right) > -_ddelta;
  }

  /**
   * Template for sharing the non-normal floating point comparisons.
   * 
   */
  template <typename T>
  inline bool
  compare_non_normals(const T& left, const T& right, bool& result)
  {
    // if equal, then short circuit the rest.  this works for INFINITY, since
    // INF==INF and -INF==-INF, and it also may avoid some extra computation
    // steps for the ulps and delta comparisons.
    if (left == right)
      result = true;
    else if (_nans_equal && isnan(left) && isnan(right))
      result = (signbit(left) == signbit(right));
    else
      return false;
    return true;
  }

private:

  float _fdelta;
  double _ddelta;

  int _nulps;
  bool _nans_equal{false};

  bool (compare_floating_point::*_float_equal)(float left, float right);
  bool (compare_floating_point::*_double_equal)(double left, double right);

};


/**
 * Test two doubles for equality using the current comparison scheme
 * and parameters.
 **/
template <>
inline bool
compare_floating_point::
near_equal(const double& left, const double& right)
{
  bool result;
  if (compare_non_normals(left, right, result))
    return result;
  return (this->*_double_equal)(left, right);
}

/**
 * Test two floats for equality using the current comparison scheme and
 * parameters.
 **/
template <>
inline bool
compare_floating_point::
near_equal(const float& left, const float& right)
{
  bool result;
  if (compare_non_normals(left, right, result))
    return result;
  return (this->*_float_equal)(left, right);
}

#endif // _compare_numbers_h_

