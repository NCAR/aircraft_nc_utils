// -*- C++ -*-

#ifndef _ReportStyle_h_
#define _ReportStyle_h_

#include <string>
#include <iosfwd>

/**
 * ReportStyle provides parameters and formatting for rendering netcdf
 * elements and comparisons in a report, such as indent length and line
 * prefix symbols.
 **/
class ReportStyle
{
public:
  ReportStyle(int indent=4);

  void
  showEqual(bool flag)
  {
    _show_equal = flag;
  }

  bool
  getShowEqual() const
  {
    return _show_equal;
  }

  void
  showIndex(bool flag)
  {
    _show_index = flag;
  }

  bool
  getShowIndex() const
  {
    return _show_index;
  }

  void
  useRightBlanks(bool flag)
  {
    _use_right_blanks = flag;
  }

  bool
  getUseRightBlanks() const
  {
    return _use_right_blanks;
  }

  void
  setReportLimit(int limit)
  {
    _report_limit = limit;
  }

  int
  getReportLimit() const
  {
    return _report_limit;
  }

  void
  showMinMax(bool enable)
  {
    _minmax = enable;
  }

  bool
  getShowMinMax() const
  {
    return _minmax;
  }

  /**
   * Render the symbols string merged with the current indent to the output
   * stream.
   **/
  std::ostream&
  prefix(std::ostream& out) const;

  /**
   * Return a new ReportStyle with the indent increased by step and
   * optionally with new symbols to be merged into the line prefix.
   **/
  ReportStyle
  derive(int step, const std::string& symbols="") const
  {
    ReportStyle copy(*this);
    copy.stepLevel(step);
    if (symbols.length())
    {
      copy._symbols = symbols;
    }
    return copy;
  }

  ReportStyle
  merge(const std::string& symbols) const
  {
    ReportStyle copy(*this);
    copy._symbols = symbols;
    return copy;
  }

  void
  stepLevel(int step)
  {
    _level += step;
  }

  void
  setIndent(int indent)
  {
    _indent = indent;
  }

  int
  getIndent()
  {
    return _indent;
  }

  static int DEFAULT_REPORT_LIMIT;

private:
  std::string _symbols;
  int _indent;
  int _level;
  bool _show_equal;
  bool _show_index;
  bool _use_right_blanks;
  int _report_limit;
  bool _minmax;
};


/**
 * Render the ReportStyle prefix to the output stream.
 **/
inline std::ostream&
operator<<(std::ostream& out, const ReportStyle& style)
{
  style.prefix(out);
  return out;
}




#endif // _ReportStyle_h_

