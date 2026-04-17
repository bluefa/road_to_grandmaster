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

const int N = 2e5 + 15;

int cc[N];
long long res = 0;

vector<int> divs[N];

bool isPrime[N];

void initDivisors()
{
    for (int i = 2; i < N; ++i)
    {
        for (int j = i; j < N; j += i)
        {
            divs[j].push_back(i);
        }
    }
}

void initPrime()
{
    memset(isPrime, 1, sizeof(isPrime));
    for (int i = 2; i < N; ++i)
    {
        if (isPrime[i])
        {
            for (int j = i + i; j < N; j += i)
            {
                isPrime[j] = false;
            }
        }
    }
}

int euclidNums[N];

void initEuclid()
{
    fill(euclidNums, euclidNums + N, 1);
    for (int i = 2; i < N; ++i)
    {
        if (isPrime[i])
        {
            for (int j = i + i; j < N; j += i)
            {
                euclidNums[j] *= -1;
                if ((j / i) % i == 0)
                {
                    euclidNums[j] = 0;
                }
            }
        }
    }
}

void addNumber(int x)
{
    for (int div : divs[x])
    {
        ++cc[div];
        res += cc[div] * euclidNums[div];
    }
}

void minusNumber(int x)
{
    for (int div : divs[x])
    {
        res -= cc[div] * euclidNums[div];
        --cc[div];
    }
}

void solve2()
{
    initPrime();
    initDivisors();
    initEuclid();

    int n;
    scanf("%d ", &n);
    vector<int> P(n + 1);
    for (int i = 1; i <= n; ++i)
    {
        scanf("%d ", &P[i]);
    }
    long long cur = 0LL;

    for (int i = 2; i <= n; ++i)
    {
        for (int j = i; j <= n; j += i)
        {
            addNumber(P[j]);
        }
        cur += res;
        for (int j = i; j <= n; j += i)
        {
            addNumber(P[j]);
        }
    }
    printf("%lld\n", cur);
}

void solve()
{
    // init();
    // int t;
    // scanf("%d",&t);
    // while(t--)
    solve2();
}

int main()
{
    // cin,cout fast

    // ios_base::sync_with_stdio(false);

    solve();
    return 0;
}
