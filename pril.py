import discord
from aiohttp import web
from discord.ext import commands
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio
import time
import os

bot = commands.Bot(command_prefix='!')
client = discord.Client()

user = []           # 유저가 입력한 노래 제목
musictitle = []     # 갈무리한 노래 제목
song_queue = []     # 갈무리한 노래 링크
musicnow = []       # 현재 재생 중인 노래


def title(msg):
    global music

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    chromedriver_dir = r"D:\chromedriver.exe"
    driver = webdriver.Chrome(chromedriver_dir, options=options)
    driver.get("https://www.youtube.com/results?search_query=" + msg + "+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music=entireNum.text.strip()

    musictitle.append(music)
    musicnow.append(music)
    test1=entireNum.get('href')
    url='https://www.youtube.com'+test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL=info['formats'][0]['url']

    driver.quit()

    return music, URL


def play(ctx):
    global vc

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))


def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

    else:
        if not vc.is_playing():
            client.loop.creat_task(vc.disconnect())


def load_chrome_driver():
    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)

@bot.event
async def on_ready():
    print('다음으로 로그인합니다.: ')
    print(bot.user.name)
    print('connection was successful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("대기"))

    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')


@bot.command()
async def 따라하기(ctx, *, text):
    await ctx.send(embed = discord.Embed(title = '따라하기', description= text, color = 0x00ff00))


@bot.command()
async def 들(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않습니다.")


@bot.command()
async def 나(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("이미 그 채널에 속해있지 않습니다.")


@bot.command()
async def 재생_URL(ctx, *, url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 - reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]["url"]
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ctx.send(embed=discord.Embed(title="노래 재생", discription="현재 " + url + "을 재생하고 있습니다.", color=0x00ff00))
    else:
        await ctx.send("노래가 이미 재생되고 있습니다.")


@bot.command()
async def 재생(ctx, *, msg):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않습니다.")

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        #chromedriver_dir = "D:\chromedriver.exe"
        driver = load_chrome_driver()
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl

        driver.quit()

        musicnow.insert(0, entireText)

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed=discord.Embed(title="노래 재생", description="현재 " + musicnow[0] + "재생 중 입니다.", color=0x00ff00))
        #vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        #await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없습니다.")
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send("대기열에 추가 : " + result)


@bot.command()
async def 일시정지(ctx):
    if vc.is_playing():
        vc.pause()
        await ctx.send(embed=discord.Embed(title="일시정지", description=musicnow[0] + " 일시정지", color=0x00ff00))
    else:
        await ctx.send("재생 중인 노래가 없습니다.")


@bot.command()
async def 다시재생(ctx):
    try:
        vc.resume()
    except:
        await ctx.send("재생 중인 노래가 없습니다.")
    else:
        await ctx.send(embed=discord.Embed(title="다시재생", description=musicnow[0] + "을(를) 다시 재생했습니다.", color=0x00ff00))


@bot.command()
async def 정지(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed=discord.Embed(title="정지", description=musicnow[0] + " 정지", color=0x00ff00))
    else:
        await ctx.send("재생 중인 노래가 없습니다.")


@bot.command()
async def 재생중(ctx):
    if not vc.is_playing():
        await ctx.send("재생 중인 노래가 없습니다.")
    else:
        await ctx.send(embed=discord.Embed(title="재생 중인 곡", description="현재 " + musicnow[0] + " 재생 중", color=0x00ff00))


@bot.command()
async def 멜론(ctx):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 유저가 접속해있지 않습니다.")

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        #chromedriver_dir = "D:\chromedriver.exe"
        driver = load_chrome_driver()
        driver.get("https://www.youtube.com/results?search_query=멜론차트")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl

        driver.quit()

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed=discord.Embed(title="노래 재생", description="현재 " + entireText + "재생 중 입니다.", color=0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        await ctx.send("이미 노래가 재생 중이라 노래를 재생할 수 없습니다.")


@bot.command()
async def 추가(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + "를 재생목록에 추가했습니다.")


@bot.command()
async def 대기열삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number) - 1]
        del musicnow[int(number) - 1 + ex]

        await ctx.send("대기열이 정상적으로 삭제되었습니다.")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없어 삭제할 수 없습니다.")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다.")
            else:
                await ctx.send("숫자를 입력해주세요.")


@bot.command()
async def 목록(ctx):
    if len(musictitle) == 0:
        await ctx.send("등록된 노래가 없습니다.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])

        await ctx.send(embed=discord.Embed(title="대기열", description=Text.strip(), color=0x00ff00))


@bot.command()
async def 목록초기화(ctx):
    try:
        ex = len(musicnow) - len(user)
        del user[:]
        del musictitle[:]
        del song_queue[:]
        while True:
            try:
                del musicnow[ex]
            except:
                break
        await ctx.send(
            embed=discord.Embed(title="목록초기화", description="""목록이 정상적으로 초기화되었습니다.""", color=0x00ff00))
    except:
        await ctx.send("등록된 노래가 없습니다.")


@bot.command()
async def 목록재생(ctx):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if len(user) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있어요!")


@bot.command()
async def 도움말(ctx):
    await ctx.send(embed = discord.Embed(title='도움말',description="""
    \n!도움말 -> 뮤직봇의 모든 명령어를 볼 수 있습니다.
    \n!들 -> 뮤직봇을 자신이 속한 채널로 부릅니다.
    \n!나 -> 뮤직봇을 자신이 속한 채널에서 내보냅니다.
    \n!재생_URL [노래링크] -> 유튜브URL를 입력하면 뮤직봇이 노래를 틀어줍니다.
    (목록재생에서는 사용할 수 없습니다.)
    \n!재생 [노래이름] -> 뮤직봇이 노래를 검색해 틀어줍니다.
    \n!정지 -> 현재 재생중인 노래를 끕니다.
    !일시정지 -> 현재 재생중인 노래를 일시정지시킵니다.
    !다시재생 -> 일시정지시킨 노래를 다시 재생합니다.
    \n!재생중 -> 지금 재생되고 있는 노래의 제목을 알려줍니다.
    \n!멜론 -> 최신 멜론차트를 재생합니다.
    \n!목록 -> 이어서 재생할 노래목록을 보여줍니다.
    !목록재생 -> 목록에 추가된 노래를 재생합니다.
    !목록초기화 -> 목록에 추가된 모든 노래를 지웁니다.
    \n!대기열추가 [노래] -> 노래를 대기열에 추가합니다.
    !대기열삭제 [숫자] -> 대기열에서 입력한 숫자에 해당하는 노래를 지웁니다.""", color = 0x00ff00))


bot.run("OTI2Mzg4MTA5MjgzODUyMzE4.Yc68KA.K-vmxdlJUpNjKRO9gu4yELxCR3o")
