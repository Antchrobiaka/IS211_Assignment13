def fibonacci(n):
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
def gcd(a, b):
    if b == 0:
        return abs(a)
    else:
        return gcd(b, a % b)
def compareTo(s1, s2):
    if s1 == "" and s2 == "":
        return 0
    if s1 == "":
        return -ord(s2[0])
    if s2 == "":
        return ord(s1[0])
    if s1[0] != s2[0]:
        return ord(s1[0]) - ord(s2[0])
    else:
        return compareTo(s1[1:], s2[1:])
if __name__ == "__main__":
    print("Fibonacci Tests:")
    for i in range(10):
        print(f"fibonacci({i}) = {fibonacci(i)}")
    print("\nGCD Tests:")
    print(f"gcd(48, 18) = {gcd(48, 18)}")
    print(f"gcd(101, 103) = {gcd(101, 103)}")
    print(f"gcd(56, 98) = {gcd(56, 98)}")
    print("\nString Comparison Tests:")
    print(f"compareTo('apple', 'apple') = {compareTo('apple', 'apple')}")
    print(f"compareTo('apple', 'apricot') = {compareTo('apple', 'apricot')}")
    print(f"compareTo('banana', 'apple') = {compareTo('banana', 'apple')}")
