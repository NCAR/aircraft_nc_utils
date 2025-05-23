// -*- C++ -*-

#ifndef _NcComparison_h_
#define _NcComparison_h_

#include <string>
#include "NcCache.h"
#include <stdexcept>
#include <list>
#include "compare_numbers.h"

class CompareNetcdfException : std::runtime_error
{
public:
  CompareNetcdfException(const std::string& what):
    std::runtime_error(what)
  {}

};


class Comparison;
class CompareNetcdf;

/**
 * Compare two components of a netcdf file.  All comparisons have a basic
 * result: added, deleted, equal, or different, depending upon whether the
 * same named component exists in the left file, right file, or both.
 * Subclasses can generate different types of reports based on what is
 * being compared, such as dimensions, variables, or attributes.
 *
 * The base class stores a reference to the CompareNetcdf, which in turn
 * contains the left and right NcCache instances in case a comparison needs
 * to access the files directly.
 *
 * Comparisons go through three stages: Construction initializes the
 * references to the two objects being compared, where one of the objects
 * can be null.  The compare() method runs the comparison, saves the
 * result, and computes any related artifacts.  The text summary of the
 * comparison can be generated with report().  Report generators should not
 * generate or update any differences, only report the artifacts already
 * computed.
 **/
class Comparison
{
public:

  typedef enum Result
  {
    Unknown, Equal, Added, Deleted, Different
  }
  Result;

  Comparison(CompareNetcdf* ncf);

  /**
   * Compute the differences between the two objects and cache the result.
   **/
  Result
  compare();

  /**
   * Return the result of the last compare().
   **/
  Result
  getResult()
  {
    return _result;
  }

  /**
   * Return true when the sides are equal.
   **/
  bool
  isEqual()
  {
    return _result == Equal;
  }

  /**
   * Return true when the sides are not equal.
   **/
  bool
  isDifferent()
  {
    return _result != Equal;
  }

  /**
   * Generate a comparison report for the two objects.  Use +/- to prefix
   * object summaries which have been added or removed, or use an empty
   * prefix for objects which are identical.
   **/
  virtual std::ostream&
  generateReport(std::ostream& out, const ReportStyle& style);

  /**
   * Return a pointer to the left object.  Subclasses implement this to
   * return a nc_object pointer to the specialized instance in the
   * subclass.
   **/
  virtual nc_object*
  getLeft() = 0;

  virtual nc_object*
  getRight() = 0;

  virtual ~Comparison() {}

protected:

  /**
   * Subclasses implement this to compute all the comparison artifacts and
   * return the basic comparison result.  The default implementation just
   * compares the text summaries of the two sides.
   **/
  virtual Result
  computeDifferences();

  /**
   * Convenience method for subclasses to create a result by first checking
   * whether the object on either side is empty, meaning the result is
   * Added or Deleted.  If an object exists on both sides, then return
   * Unknown.
   **/
  Result
  compareObjects();

  CompareNetcdf* _ncf;
  Result _result;
};


/**
 * A Comparison subclass which compares some aspect of the two files and
 * not specific objects, therefore it does not have left and right objects.
 **/
class FileComparison : public Comparison
{
public:
  FileComparison(CompareNetcdf* ncf) :
    Comparison(ncf)
  {}

  virtual nc_object*
  getLeft()
  {
    return 0;
  }

  virtual nc_object*
  getRight()
  {
    return 0;
  }

  virtual std::ostream&
  generateReport(std::ostream& out, const ReportStyle& style)
  {
    throw CompareNetcdfException("FileComparison does not implement "
                                 "generateReport()");
  }

protected:
  virtual Result
  computeDifferences()
  {
    return Comparison::Unknown;
  }

};


/**
 * Compare time arrays between the two files.
 **/
class CompareTimes : public FileComparison
{
public:
  CompareTimes(CompareNetcdf* ncf);

  virtual std::ostream&
  generateReport(std::ostream& out, const ReportStyle& style);

protected:
  virtual Result
  computeDifferences();

  nc_time leftbegin;
  nc_time leftend;

  nc_time rightbegin;
  nc_time rightend;

  /// Number of times which are in common between the two files.
  unsigned int noverlap;

  /// Percentage of times in common out of union of all times.
  float percent_overlap;

  /// Times on left side which are unique.
  std::vector<nc_time> uniqueleft;

  /// Times on right side which are unique.
  std::vector<nc_time> uniqueright;

};


template <typename T>
class CompareObjects : public Comparison
{
public:
  virtual nc_object*
  getLeft()
  {
    return left;
  }

  virtual nc_object*
  getRight()
  {
    return right;
  }

protected:
  CompareObjects(CompareNetcdf* ncf, T* left_, T* right_):
    Comparison(ncf),
    left(left_),
    right(right_)
  {}

  T* left;
  T* right;
};



class CompareDimensions : public CompareObjects<nc_dimension>
{
public:
  CompareDimensions(CompareNetcdf* ncf,
                    nc_dimension* left, nc_dimension* right);

  virtual Result
  computeDifferences();
};


class CompareAttributes : public CompareObjects<nc_attribute>
{
public:
  CompareAttributes(CompareNetcdf* ncf, nc_attribute* left, nc_attribute* right);

  virtual Comparison::Result
  computeDifferences();

  virtual std::ostream&
  generateReport(std::ostream& out, const ReportStyle& style);

  using typename Comparison::Result;
  using CompareObjects<nc_attribute>::left;
  using CompareObjects<nc_attribute>::right;

  // These would only get used for numeric attributes.
  double absolute_error;
  double relative_error;
};


class CompareVariables : public CompareObjects<nc_variable>
{
public:
  CompareVariables(CompareNetcdf* ncf, nc_variable* left, nc_variable* right);

  virtual Comparison::Result
  computeDifferences();

  /**
   * If the variables differ by type, dimensions, name, or attributes, then
   * report the different definitions.  The statistical differences are
   * reported in reportStatistics().
   **/
  virtual std::ostream&
  generateReport(std::ostream& out, const ReportStyle& style);

  std::ostream&
  statisticsHeader(std::ostream& out, const ReportStyle& style);

  std::ostream&
  reportStatistics(std::ostream& out, const ReportStyle& style);

  bool
  meansNearEqual();

  using typename Comparison::Result;
  using CompareObjects<nc_variable>::left;
  using CompareObjects<nc_variable>::right;

  double absolute_error;
  double relative_error;
  // total number of points that differ
  int total_differences;
  std::vector< std::shared_ptr<CompareAttributes> > atts;
  bool dimsequal;
  variable_ranges ranges;
};



class CompareNetcdf
{
public:
  CompareNetcdf(NcCache* left, NcCache* right);

  void
  compare();

  std::ostream&
  report(std::ostream& out);

  inline NcCache*
  getLeft()
  {
    return _left;
  }

  inline NcCache*
  getRight()
  {
    return _right;
  }

  ReportStyle&
  style()
  {
    return _style;
  }

  void
  ignore(const std::vector<std::string>& ignores)
  {
    _ignores = ignores;
  }

  void
  selectVariables(const std::vector<std::string>& selects)
  {
    _selects = selects;
  }

  /**
   * This is just a convenient wrapper to the compare_floating_point
   * template method.
   **/
  template <typename T>
  inline bool
  near_equal(const T& left, const T& right)
  {
    return _comparator.near_equal(left, right);
  }

  void
  setFloatComparator(const compare_floating_point& cfp)
  {
    _comparator = cfp;
  }

  int
  countDifferences();

  bool
  isIgnored(const std::string& name);

  /**
   * If name matches one of the select patterns or there are no selections,
   * the name is selected, unless it matches one of the ignore patterns.
   **/
  bool
  isSelected(const std::string& name);

  void
  addWarning(const std::string, const std::string& msg)
  {
    _warnings.push_back(msg);
  }

  std::vector<std::string>
  getWarnings()
  {
    return _warnings;
  }

private:

  void
  compareVariables();

  void
  compareDimensions();

  void
  compareAttributes();

  NcCache* _left;
  NcCache* _right;
  std::vector<std::string> _ignores;
  std::vector<std::string> _selects;

  std::vector< std::shared_ptr<CompareDimensions> > dims;
  std::vector< std::shared_ptr<CompareVariables> > vars;

  // Global attribute comparisons.
  std::vector< std::shared_ptr<CompareAttributes> > atts;

  CompareTimes times;

  std::vector<std::string> _warnings;

  compare_floating_point _comparator;

  ReportStyle _style;
};


bool
match_substring(const std::string& pattern, const std::string& text);


#endif // _NcComparison_h_
