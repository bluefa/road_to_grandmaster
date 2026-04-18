#ifndef _GLIBCXX_NO_ASSERT
#include <cassert>
#endif
#include <cctype>
#include <cerrno>
#include <cfloat>
#include <ciso646>
#include <climits>
#include <clocale>
#include <cmath>
#include <csetjmp>
#include <csignal>
#include <cstdarg>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>

#if __cplusplus >= 201103L
#include <ccomplex>
#include <cfenv>
#include <cinttypes>
#include <cstdbool>
#include <cstdint>
#include <ctgmath>
#include <cwchar>
#include <cwctype>
#endif

// C++
#include <algorithm>
#include <bitset>
#include <complex>
#include <deque>
#include <exception>
#include <fstream>
#include <functional>
#include <iomanip>
#include <ios>
#include <iosfwd>
#include <iostream>
#include <istream>
#include <iterator>
#include <limits>
#include <list>
#include <locale>
#include <map>
#include <memory>
#include <new>
#include <numeric>
#include <ostream>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <streambuf>
#include <string>
#include <typeinfo>
#include <utility>
#include <valarray>
#include <vector>

#if __cplusplus >= 201103L
#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <forward_list>
#include <future>
#include <initializer_list>
#include <mutex>
#include <random>
#include <ratio>
#include <regex>
#include <scoped_allocator>
#include <system_error>
#include <thread>
#include <tuple>
#include <typeindex>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#endif

#include <ranges>

#define ll long long
using namespace std;

const int N = 3e5 + 15;

int h[N];
ll hPre[N];

int mr[N], ml[N];

void solve2()
{
    int n;
    scanf("%d ", &n);
    for (int i = 1; i <= n; ++i)
    {
        scanf("%d ", &h[i]);
        hPre[i] = hPre[i - 1] + h[i];
    }
    for (int i = n; i; --i)
    {
        if (i == n)
        {
            mr[i] = i;
        }
        else
        {
            mr[i] = (h[i] - 1 >= h[i + 1]) ? mr[i + 1] : i;
        }
    }

    for (int i = 1; i <= n; ++i)
    {
        if (i == 1)
        {
            ml[i] = 1;
        }
        else
        {
            ml[i] = (h[i] - 1 >= h[i - 1]) ? ml[i - 1] : i;
        }
    }
    ll res = accumulate(h + 1, h + n + 1, 0LL);

    for (int exp = 1; exp <= n; ++exp)
    {
        int l = ml[exp], r = mr[exp];
        ll tmp = hPre[n] - (hPre[r] - hPre[l - 1]) + h[exp];

        if (1 < l)
        {
            tmp -= h[l] - 1;
        }
        if (r < n)
        {
            tmp -= h[r] - 1;
        }
        res = min(res, tmp);
    }

    printf("%lld\n", res);
}

void solve()
{
    // init();
    int t;
    scanf("%d", &t);
    while (t--)
        solve2();
}

int main()
{
    // cin,cout fast

    // ios_base::sync_with_stdio(false);

    solve();
    return 0;
}
