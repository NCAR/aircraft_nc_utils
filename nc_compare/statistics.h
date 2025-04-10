
#ifndef _statistics_hh_
#define _statistics_hh_

namespace statistics {

template <typename T>
void
mean_min_max(T* mean, T* min, T* max, const T* begin, size_t n)
{
  if (n == 0)
  {
    return;
  }
  T sum = *min = *max = *begin;
  for (const T* p = begin+1; p != begin+n; ++p)
  {
    if (*p < *min)
      *min = *p;
    if (*p > *max)
      *max = *p;
    sum += *p;
  }
  *mean = sum / n;
}

}

#endif // _statistics_hh_
