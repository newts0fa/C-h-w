#include <iostream>
#include <cmath>
#include <limits>
using namespace std;
int main()
{
	float s;
	float x;
	float y;
	cin >> x;
	cin >> y;
	double result;

	result = 0.125 * abs((sin(x)/y));
	cout  << result << endl;

	float i, j, res;
	cin >> i;
	cin >> j;
	res = pow(2, j);
	double lg = log10(res);
	cout << lg << endl;


	cout << fmax(result,lg) << endl;


}
