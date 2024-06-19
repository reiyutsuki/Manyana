import asyncio
import os
import random
import re
#注释
import yaml
from mirai import logger
from plugins.chatGLMonline import  glm4
from plugins.cozeBot import cozeBotRep
from plugins.googleGemini import geminirep
from plugins.ReplyModels import gptOfficial, gptUnofficial, kimi, qingyan, lingyi, stepAI, qwen, gptvvvv, grop, \
    gpt4hahaha, localAurona, anotherGPT35, chatGLM,lolimigpt2, relolimigpt2
from plugins.RandomStr import random_str
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, superVG


with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
CoziUrl = resulttr.get("cozi")
gptdev = resulttr.get("gpt3.5-dev")
geminiapikey = resulttr.get("gemini")
proxy = resulttr.get("proxy")

GeminiRevProxy = resulttr.get("GeminiRevProxy")
berturl = resulttr.get("bert_colab")
if proxy != "":
    os.environ["http_proxy"] = proxy
gptkeys = resulttr.get("openai-keys")
chatGLM_api_key = resulttr.get("chatGLM")
with open('config.json', 'r', encoding='utf-8') as f:
    data = yaml.load(f.read(), Loader=yaml.FullLoader)
config = data
mainGroup = int(config.get("mainGroup"))
botName = config.get("botName")
botqq=int(config.get("botQQ"))
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
voicegg = result.get("语音功能设置").get("voicegenerate")
friendsAndGroups = result.get("加群和好友")
trustDays = friendsAndGroups.get("trustDays")
glmReply = result.get("chatGLM").get("glmReply")
privateGlmReply = result.get("chatGLM").get("privateGlmReply")
randomModelPriority = result.get("chatGLM").get("random&PriorityModel")
replyModel = result.get("chatGLM").get("model")
trustglmReply = result.get("chatGLM").get("trustglmReply")
maxPrompt = result.get("chatGLM").get("maxPrompt")
voiceLangType = str(result.get("语音功能设置").get("voiceLangType"))
allcharacters = result.get("chatGLM").get("bot_info")
maxTextLen = result.get("chatGLM").get("maxLen")
voiceRate = result.get("chatGLM").get("voiceRate")
speaker = result.get("语音功能设置").get("speaker")
withText = result.get("chatGLM").get("withText")
newLoop = asyncio.new_event_loop()
with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
    cha = yaml.load(f.read(), Loader=yaml.FullLoader)
chatGLMData = cha
async def tstt(r):
    data1 = {}
    data1['speaker'] = speaker
    st8 = re.sub(r"（[^）]*）", "", r)  # 使用r前缀表示原始字符串，避免转义字符的问题
    data1["text"] = st8
    if voicegg == "vits":
        logger.info("调用vits语音回复")

        path = 'data/voices/' + random_str() + '.wav'
        if voiceLangType == "<jp>":
            texts = await translate(str(st8))
            tex = '[JA]' + texts + '[JA]'
        else:
            tex = "[ZH]" + st8 + "[ZH]"
        logger.info("启动文本转语音：text: " + tex + " path: " + path)
        # spe = rte.get("defaultModel").get("speaker")
        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
            resulte = yaml.load(f.read(), Loader=yaml.FullLoader)
        spe = resulte.get("defaultModel").get("speaker")
        modelSelect = resulte.get("defaultModel").get("modelSelect")
        await voiceGenerate({"text": tex, "out": path, "speaker": spe, "modelSelect": modelSelect})
    else:
        logger.info(f"调用{voicegg}语音合成")
        path = await superVG(data1, voicegg, berturl, voiceLangType)
    return path

async def loop_run_in_executor(executor, func, *args):
    try:
        r = await executor.run_in_executor(None, func, *args)
        logger.info(f"并发调用 | successfully running funcname：{func.__name__} result：{r.get('content')}")
        return [str(func.__name__), r]
    except Exception as e:
        # logger.error(f"Error running {func.__name__}: {e}")
        return [str(func.__name__), None]
# 运行异步函数
async def modelReply(senderName,senderId, text,modelHere, trustUser):
    logger.info(modelHere)
    try:
            if type(allcharacters.get(modelHere)) == dict:
                with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                    resy = yaml.load(f.read(), Loader=yaml.FullLoader)
                meta1 = resy.get("chatGLM").get("bot_info").get(modelHere)
                meta1["user_name"] = senderName
                meta1["user_info"] = meta1.get("user_info").replace("【用户】", senderName).replace("【bot】",
                                                                                                              botName)
                meta1["bot_info"] = meta1.get("bot_info").replace("【用户】", senderName).replace("【bot】",
                                                                                                            botName)
                meta1["bot_name"] = botName
                bot_in = meta1
            else:
                bot_in = str("你是" + botName + ",我是" + senderName + "," + allcharacters.get(
                    modelHere)).replace("【bot】",
                                        botName).replace("【用户】", senderName)
    except Exception as e:
        logger.error(e)
        logger.info(f"无法获取到该用户昵称 id：{senderId}")
        try:
            bot_in = str("你是" + botName + allcharacters.get(
                modelHere)).replace("【bot】",
                                    botName).replace("【用户】", "我")
        except:
            return "模型不可用，请发送 可用角色模板 并重新设定模型"
    try:
        loop = asyncio.get_event_loop()

        if text == "" or text == " ":
            text = "在吗"

        if senderId in chatGLMData:
            prompt1 = chatGLMData.get(senderId)
            prompt1.append({"content": text, "role": "user"})
        else:
            prompt1 = [{"content": text, "role": "user"}]
            if modelHere == "anotherGPT3.5" or modelHere == "random":
                try:
                    rep = await loop.run_in_executor(None, anotherGPT35, [{"role": "user", "content": bot_in}],
                                                     senderId)
                except:
                    logger.error("初始化anotherGPT3.5失败")
        logger.info(f"{modelHere}  bot 接受提问：" + text)

        if modelHere == "random":
            tasks = []
            logger.warning("请求所有模型接口")
            # 将所有模型的执行代码包装成异步任务，并添加到任务列表
            # tasks.append(loop_run_in_executor(loop, gptUnofficial if gptdev else gptOfficial, prompt1, gptkeys, proxy,bot_in))
            tasks.append(loop_run_in_executor(loop, cozeBotRep, CoziUrl, prompt1, proxy))
            tasks.append(loop_run_in_executor(loop, kimi, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, qingyan, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, grop, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, lingyi, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, relolimigpt2, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, stepAI, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, qwen, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, gptvvvv, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, gpt4hahaha, prompt1, bot_in))
            tasks.append(loop_run_in_executor(loop, anotherGPT35, prompt1, senderId))
            # tasks.append(loop_run_in_executor(loop,localAurona,prompt1,bot_in))
            # ... 添加其他模型的任务 ...
            aim = {"role": "user", "content": bot_in}
            prompt1 = [i for i in prompt1 if i != aim]
            aim = {"role": "assistant", "content": "好的，已了解您的需求~我会扮演好您设定的角色。"}
            prompt1 = [i for i in prompt1 if i != aim]

            done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            reps = {}
            # 等待所有任务完成
            rep = None
            for task in done:
                result = task.result()[1]
                if result is not None:
                    if "content" not in result:
                        continue
                    if "无法解析" in result.get("content") or "账户余额不足" in result.get("content") or "令牌额度" in result.get(
                            "content") or "敏感词汇" in result.get("content") or "request id" in result.get(
                        "content") or "This model's maximum" in result.get(
                        "content") or "solve CAPTCHA to" in result.get("content") or "输出错误请联系站长" in result.get(
                        "content") or "接口失败" in result.get("content") or "ip请求过多" in result.get(
                        "content") or "第三方响应错误" in result.get("content"):
                        continue
                    reps[task.result()[0]] = task.result()[1]
                    # reps.append(task.result())  # 添加可用结果

            # 如果所有任务都完成但没有找到非None的结果
            if len(reps) == 0:
                logger.warning("所有模型都未能返回有效回复")
                raise Exception
            # print(reps)
            modeltrans = {"gptX": "gptvvvv", "清言": "qingyan", "通义千问": "qwen", "anotherGPT3.5": "anotherGPT35",
                          "lolimigpt": "relolimigpt2", "step": "stepAI"}
            for priority in randomModelPriority:
                if priority in modeltrans:
                    priority = modeltrans.get(priority)
                if priority in reps:
                    rep = reps.get(priority)
                    logger.info(f"random模型选择结果：{priority}: {rep}")
                    break
        if modelHere == "gpt3.5":
            if gptdev == True:
                rep = await loop.run_in_executor(None, gptUnofficial, prompt1, gptkeys, proxy, bot_in)
            else:
                rep = await loop.run_in_executor(None, gptOfficial, prompt1, gptkeys, proxy, bot_in)
        elif modelHere == "anotherGPT3.5":
            rep = await loop.run_in_executor(None, anotherGPT35, prompt1, senderId)
        elif modelHere == "Cozi":
            rep = await loop.run_in_executor(None, cozeBotRep, CoziUrl, prompt1, proxy)
        elif modelHere == "kimi":
            rep = await loop.run_in_executor(None, kimi, prompt1, bot_in)
        elif modelHere == "清言":
            rep = await loop.run_in_executor(None, qingyan, prompt1, bot_in)
        elif modelHere == "lingyi":
            rep = await loop.run_in_executor(None, lingyi, prompt1, bot_in)
        elif modelHere == "step":
            rep = await loop.run_in_executor(None, stepAI, prompt1, bot_in)
        elif modelHere == "通义千问":
            rep = await loop.run_in_executor(None, qwen, prompt1, bot_in)
        elif modelHere == "gptX":
            rep = await loop.run_in_executor(None, gptvvvv, prompt1, bot_in)
        elif modelHere == "grop":
            rep = await loop.run_in_executor(None, grop, prompt1, bot_in)
        elif modelHere == "aurora":
            rep = await loop.run_in_executor(None, localAurona, prompt1, bot_in)
        elif modelHere == "lolimigpt":
            rep = await lolimigpt2(prompt1, bot_in)
            if "令牌额度" in rep.get("content"):
                logger.error("没金币了喵")
                return "api没金币了喵\n请发送 @bot 可用角色模板 以更换其他模型"
            if "敏感词汇" in rep.get("content"):
                logger.error("敏感词了搁这")
                try:
                    chatGLMData.pop(senderId)
                except Exception as e:
                    logger.error(e)
                return

        elif modelHere == "glm-4":
            rep = await glm4(prompt1, bot_in)
            if "禁止违规问答" == rep.get("content"):
                logger.error("敏感喽，不能用了")
                try:
                    chatGLMData.pop(senderId)
                except Exception as e:
                    logger.error(e)
                return "触发了敏感内容审核，已自动清理聊天记录"

        elif modelHere == "Gemini":
            r = await geminirep(ak=random.choice(geminiapikey), messages=prompt1, bot_info=bot_in,GeminiRevProxy=GeminiRevProxy),
            #print(r,type(r))
            rep = {"role": "assistant", "content": r[0].replace(r"\n","\n")}
        elif type(allcharacters.get(modelHere)) == dict:
            if str(senderId) not in trustUser and trustglmReply:
                return "无模型使用权限！"
            else:
                r = await loop.run_in_executor(None, chatGLM, chatGLM_api_key, bot_in, prompt1)
                rep = {"role": "assistant", "content": r}
        prompt1.append(rep)
        # 超过10，移除第一个元素
        if len(prompt1) > maxPrompt:
            logger.warning(f"{modelHere} prompt超限，移除元素")
            del prompt1[0]
            del prompt1[0]
        chatGLMData[senderId] = prompt1
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        #print(rep.get('content'),type(rep.get('content')))
        logger.info(f"{modelHere} bot 回复：" + rep.get('content'))
        return rep.get("content")
        #await tstt(rep.get('content'), event)
    except Exception as e:
        logger.error(e)
        try:
            chatGLMData.pop(senderId)
        except Exception as e:
            logger.error("清理用户prompt出错")
        return "出错，请重试\n或发送 \n@bot 可用角色模板\n 以更换其他模型"
async def clearsinglePrompt(senderid):
    try:
        chatGLMData.pop(senderid)
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        return "已清理近期记忆"
    except:
        logger.error("清理缓存出错，无本地对话记录")
        return "无本地对话记录"
async def clearAllPrompts():
    try:
        chatGLMData = {"f": "hhh"}
        # chatGLMData.pop(event.sender.id)
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        return "已清除所有用户的prompt"
    except:
        return "清理缓存出错，无本地对话记录"
