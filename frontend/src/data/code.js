export const codeSamples = {
  'REST API Authentication': `function authenticate(req, res, next) {\n  const token = req.headers['authorization'];\n  if (!token) return res.status(401).json({ error: 'No token provided' });\n  try {\n    req.user = verifyToken(token);\n    next();\n  } catch (err) {\n    res.status(403).json({ error: 'Invalid token' });\n  }\n}`,
  'Debounce Utility': `function debounce(fn, delay) {\n  let timer;\n  return (...args) => {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), delay);\n  };\n}`,
  'Binary Search': `def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1`,
};

export const initialSnippets = [
  { id: 's1', title: 'REST API Authentication', desc: 'JWT auth middleware for Express routes.', lang: 'JavaScript', isPublic: true, created: '3 days ago', updated: '1 day ago',
    code: codeSamples['REST API Authentication'],
    versions: [{ v: 2, msg: 'Added token expiry handling', time: '1 day ago' }, { v: 1, msg: 'Initial version', time: '3 days ago' }] },
  { id: 's2', title: 'Debounce Utility', desc: 'Generic debounce helper for input handlers.', lang: 'JavaScript', isPublic: true, created: '1 week ago', updated: '6 days ago',
    code: codeSamples['Debounce Utility'],
    versions: [{ v: 1, msg: 'Initial version', time: '1 week ago' }] },
  { id: 's3', title: 'Binary Search', desc: 'Iterative binary search implementation.', lang: 'Python', isPublic: false, created: '2 weeks ago', updated: '2 weeks ago',
    code: codeSamples['Binary Search'],
    versions: [{ v: 1, msg: 'Initial version', time: '2 weeks ago' }] },
];

export const problemsData = [
  { id: 'p1', title: 'Two Sum', diff: 'Easy', tags: ['Arrays', 'Hash Map'], desc: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.', examples: [{ in: 'nums=[2,7,11,15], target=9', out: '[0,1]' }], constraints: '2 ≤ nums.length ≤ 10⁴', starter: 'def two_sum(nums, target):\n    # your code here\n    pass' },
  { id: 'p2', title: 'Reverse String', diff: 'Easy', tags: ['Strings', 'Two Pointers'], desc: 'Write a function that reverses a string in place.', examples: [{ in: 's="hello"', out: '"olleh"' }], constraints: '1 ≤ s.length ≤ 10⁵', starter: 'def reverse_string(s):\n    # your code here\n    pass' },
  { id: 'p3', title: 'Valid Parentheses', diff: 'Easy', tags: ['Stack', 'Strings'], desc: 'Determine if the input string of brackets is valid.', examples: [{ in: 's="()[]{}"', out: 'true' }], constraints: '1 ≤ s.length ≤ 10⁴', starter: 'def is_valid(s):\n    # your code here\n    pass' },
  { id: 'p4', title: 'Palindrome Number', diff: 'Easy', tags: ['Math'], desc: 'Determine whether an integer is a palindrome without converting it to a string.', examples: [{ in: 'x=121', out: 'true' }], constraints: '-2³¹ ≤ x ≤ 2³¹-1', starter: 'def is_palindrome(x):\n    # your code here\n    pass' },
  { id: 'p5', title: 'Maximum Subarray', diff: 'Easy', tags: ['Arrays', 'DP'], desc: 'Find the contiguous subarray with the largest sum.', examples: [{ in: 'nums=[-2,1,-3,4,-1,2,1,-5,4]', out: '6' }], constraints: '1 ≤ nums.length ≤ 10⁵', starter: 'def max_subarray(nums):\n    # your code here\n    pass' },
  { id: 'p6', title: 'Longest Substring Without Repeating Characters', diff: 'Medium', tags: ['Strings', 'Sliding Window'], desc: 'Find the length of the longest substring without repeating characters.', examples: [{ in: 's="abcabcbb"', out: '3' }], constraints: '0 ≤ s.length ≤ 5×10⁴', starter: 'def length_of_longest_substring(s):\n    # your code here\n    pass' },
  { id: 'p7', title: 'Merge Intervals', diff: 'Medium', tags: ['Arrays', 'Sorting'], desc: 'Merge all overlapping intervals.', examples: [{ in: '[[1,3],[2,6],[8,10]]', out: '[[1,6],[8,10]]' }], constraints: '1 ≤ intervals.length ≤ 10⁴', starter: 'def merge(intervals):\n    # your code here\n    pass' },
  { id: 'p8', title: 'Product of Array Except Self', diff: 'Medium', tags: ['Arrays'], desc: 'Return an array where each element is the product of all other elements.', examples: [{ in: 'nums=[1,2,3,4]', out: '[24,12,8,6]' }], constraints: '2 ≤ nums.length ≤ 10⁵', starter: 'def product_except_self(nums):\n    # your code here\n    pass' },
  { id: 'p9', title: 'Group Anagrams', diff: 'Medium', tags: ['Strings', 'Hash Map'], desc: 'Group strings that are anagrams of each other.', examples: [{ in: '["eat","tea","tan","ate","nat","bat"]', out: '[["eat","tea","ate"],["tan","nat"],["bat"]]' }], constraints: '1 ≤ strs.length ≤ 10⁴', starter: 'def group_anagrams(strs):\n    # your code here\n    pass' },
  { id: 'p10', title: 'Search in Rotated Sorted Array', diff: 'Medium', tags: ['Binary Search'], desc: 'Search a target value in a rotated sorted array.', examples: [{ in: 'nums=[4,5,6,7,0,1,2], target=0', out: '4' }], constraints: '1 ≤ nums.length ≤ 5000', starter: 'def search(nums, target):\n    # your code here\n    pass' },
  { id: 'p11', title: 'Trapping Rain Water', diff: 'Hard', tags: ['Arrays', 'Two Pointers'], desc: 'Compute how much water can be trapped after raining given elevation heights.', examples: [{ in: 'height=[0,1,0,2,1,0,1,3,2,1,2,1]', out: '6' }], constraints: '1 ≤ height.length ≤ 2×10⁴', starter: 'def trap(height):\n    # your code here\n    pass' },
  { id: 'p12', title: 'Merge K Sorted Lists', diff: 'Hard', tags: ['Linked List', 'Heap'], desc: 'Merge k sorted linked lists into one sorted list.', examples: [{ in: 'lists=[[1,4,5],[1,3,4],[2,6]]', out: '[1,1,2,3,4,4,5,6]' }], constraints: '0 ≤ k ≤ 10⁴', starter: 'def merge_k_lists(lists):\n    # your code here\n    pass' },
  { id: 'p13', title: 'Longest Valid Parentheses', diff: 'Hard', tags: ['Stack', 'DP'], desc: 'Find the length of the longest valid parentheses substring.', examples: [{ in: 's=")()())"', out: '4' }], constraints: '0 ≤ s.length ≤ 3×10⁴', starter: 'def longest_valid_parentheses(s):\n    # your code here\n    pass' },
  { id: 'p14', title: 'Climbing Stairs', diff: 'Easy', tags: ['DP'], desc: 'Count distinct ways to climb n stairs taking 1 or 2 steps at a time.', examples: [{ in: 'n=3', out: '3' }], constraints: '1 ≤ n ≤ 45', starter: 'def climb_stairs(n):\n    # your code here\n    pass' },
  { id: 'p15', title: 'Number of Islands', diff: 'Medium', tags: ['Graph', 'DFS'], desc: 'Count the number of islands in a 2D grid.', examples: [{ in: 'grid=[["1","1","0"],["0","1","0"]]', out: '1' }], constraints: '1 ≤ rows, cols ≤ 300', starter: 'def num_islands(grid):\n    # your code here\n    pass' },
  { id: 'p16', title: 'Course Schedule', diff: 'Medium', tags: ['Graph', 'Topological Sort'], desc: 'Determine if it is possible to finish all courses given prerequisites.', examples: [{ in: 'numCourses=2, prerequisites=[[1,0]]', out: 'true' }], constraints: '1 ≤ numCourses ≤ 2000', starter: 'def can_finish(numCourses, prerequisites):\n    # your code here\n    pass' },
];

export const initialSolvedProblems = ['p1', 'p3', 'p14'];

export const badgeDefs = [
  { id: 'first', name: 'First Solution', desc: 'Solve your first coding problem.', check: (s) => s.solved.length >= 1 },
  { id: 'ten', name: '10 Problems Solved', desc: 'Solve 10 coding problems.', check: (s) => s.solved.length >= 10 },
  { id: 'twentyfive', name: '25 Problems Solved', desc: 'Solve 25 coding problems.', check: (s) => s.solved.length >= 25 },
  { id: 'creator', name: 'Snippet Creator', desc: 'Create your first code snippet.', check: (s) => s.snippets.length >= 1 },
  { id: 'multilang', name: 'Multi-Language Developer', desc: 'Use 2 or more languages across your snippets.', check: (s) => new Set(s.snippets.map((x) => x.lang)).size >= 2 },
  { id: 'solver', name: 'Problem Solver', desc: 'Solve 3 coding problems.', check: (s) => s.solved.length >= 3 },
];

export const monacoLangMap = { JavaScript: 'javascript', Python: 'python', Java: 'java', 'C++': 'cpp', C: 'c', HTML: 'html', CSS: 'css', SQL: 'sql' };

/** Deterministic mock "execution" — same heuristic as the original HTML demo. */
export function evaluateMockSubmission(code) {
  const trimmed = (code || '').trim();
  if (!trimmed) return { status: 'compile_error', error: 'SyntaxError: unexpected end of input (empty submission).' };
  if (trimmed.length < 20) return { status: 'wrong', error: 'AssertionError: expected [0, 1], got None on Test 2.' };
  const hasReturn = /return/.test(trimmed);
  if (!hasReturn) return { status: 'runtime_error', error: 'RuntimeError: function did not return a value.' };
  return { status: 'accepted', runtime: `${(Math.random() * 60 + 20).toFixed(0)} ms`, memory: `${(Math.random() * 8 + 12).toFixed(1)} MB` };
}
