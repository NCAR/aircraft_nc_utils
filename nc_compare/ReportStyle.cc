
#include "ReportStyle.h"
#include <iostream>
#include <iomanip>

int ReportStyle::DEFAULT_REPORT_LIMIT = 10;

ReportStyle::
ReportStyle(int indent):
  _indent(indent),
  _level(0),
  _show_equal(false),
  _show_index(false),
  _use_right_blanks(false),
  _report_limit(DEFAULT_REPORT_LIMIT),
  _minmax(false),
  _show_times(false)
{}


std::ostream&
ReportStyle::
prefix(std::ostream& out) const
{
  out << std::setw(_level*_indent) << std::left << _symbols;
  return out;
}



