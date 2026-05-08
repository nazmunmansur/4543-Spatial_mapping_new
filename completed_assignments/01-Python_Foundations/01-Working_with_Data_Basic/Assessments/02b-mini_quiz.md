# ❓ Mini Quiz: 02 - Working with Data

Test your memory and skills from this module!

---

### 1. Which list method removes an element by value?
By using the remove()method. for example:
L = [13,17,31,37,73]
L.remove(17)# will remove the value 17. 
---

### 2. How do you access the second element of a tuple?
By using the indexing method. for example: 
x = (10, 20, 30) 
x = t[1] # will access the second element of the tuple.
---

### 3. What happens if you try to change a value in a tuple?

---Tuples are immutable. So we cannot change the value of a tuple directly.

### 4. What method would you use to get all keys in a dictionary?

---The most straightforward and Pythonic way to get all keys in a dictionary is to simply iterate over the dictionary directly  

my_dict = {'apple': 1, 'banana': 2, 'cherry': 3} 
for key in my_dict: 
    print(key) 
it will show the Output: 
apple 
banana 
cherry 

### 5. What is printed?

```python
d = {'a': 1, 'b': 2}
print(d.get('c', 0))
```

Answer: It will print 0 as there is no "c" variable in the dictionary. ____
