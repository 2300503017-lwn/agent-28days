多轮对话：
   此句控制 记录AI的回答 
   messages.append({"role": "assistant", "content": reply})
   
   该句用户将用户提问记录下来，根据此句回答问题 ，注释掉后agent如同聋子一般，答非所问，不答
   messages.append({"role": "user", "content": user_input})

