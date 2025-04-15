
#ifndef _statistics_hh_
#define _statistics_hh_

#include <cmath>

namespace statistics {

template <typename T>
void
mean_min_max(T* mean, T* min, T* max, const T* begin, size_t n)
{
  if (n == 0)
  {
    return;
  }
  double sum = *min = *max = *begin;
  for (const T* p = begin+1; p != begin+n; ++p)
  {
    if (std::isnan(*min) || *p < *min)
      *min = *p;
    if (std::isnan(*max) || *p > *max)
      *max = *p;
    sum += *p;
  }
  *mean = sum / n;
}

}

#endif // _statistics_hh_
