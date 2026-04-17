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
const int B = 30;

int ne[N][B];
int a[N];

int lastSeen[B];

void updateLastSeen(int i)
{
    for (int b = 0; b < B; ++b)
    {
        if (a[i] & (1 << b))
        {
            lastSeen[b] = i;
        }
    }
}

void solve2()
{
    int n, q;
    scanf("%d %d ", &n, &q);

    fill(lastSeen, lastSeen + B, -1);

    for (int i = 1; i <= n; ++i)
    {
        scanf("%d ", &a[i]);
        fill(ne[i], ne[i] + B, N - 1);
    }

    for (int i = n; i; --i)
    {
        for (int b = 0; b < B; ++b)
        {
            if (a[i] & (1 << b))
            {
                int ind = lastSeen[b];
                if (ind != -1)
                {
                    ne[i][b] = min(ne[i][b], ind);
                    for (int j = 0; j < B; ++j)
                    {
                        ne[i][j] = min(ne[i][j], ne[ind][j]);
                    }
                }
            }
        }
        updateLastSeen(i);
    }

    for (int i = 0; i < q; ++i)
    {
        int x, y;
        scanf("%d %d ", &x, &y);

        bool find = false;
        for (int b = 0; b < B; ++b)
        {
            if (a[y] & (1 << b))
            {
                find = find | (ne[x][b] <= y);
            }
        }
        printf(find ? "Shi\n" : "Fou\n");
    }
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
