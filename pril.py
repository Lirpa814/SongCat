import discord
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

# MODE : local
# bot = commands.Bot(command_prefix='#')
#

# MODE : server
bot = commands.Bot(command_prefix='!')
#
client = discord.Client()

user = []
musictitle = []
song_queue = []
musicnow = []

send_channel_id = 889512310849277962


def title(msg):
    global music

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    # MODE : local
    # chromedriver_dir = r"D:\chromedriver.exe"
    # driver = webdriver.Chrome(chromedriver_dir, options=options)
    #

    # MODE : server
    driver = load_chrome_driver()
    #
    driver.get("https://www.youtube.com/results?search_query=" + msg + "+lyrics")
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()

    musictitle.append(music)
    musicnow.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com' + test1
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

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

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        if not vc.is_playing():
            client.loop.create_task(vc.disconnect())


@bot.event
async def on_ready():
    print(bot.user.name + ' 로그인 성공')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("열심히 작곡"))

    # MODE : local
    #

    # MODE : server
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')
    #


# MODE : local
#

# MODE : server
def load_chrome_driver():
    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)


#

@bot.command()
async def 따라해(ctx, *, text):
    await ctx.send(embed=discord.Embed(title='Follow', description=text, color=0x00ff00))


@bot.command()
async def 들(ctx):
    ch = bot.get_channel(send_channel_id)
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
        await ch.send(embed=discord.Embed(title='Hello', description="만나서 반가워요.", color=0x00ff00))
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
            await ch.send(embed=discord.Embed(title='Hello', description="만나서 반가워요.", color=0x00ff00))
        except:
            await ch.send(embed=discord.Embed(title='Notice', description="음성채널에 아무도 없어요.", color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 나(ctx):
    ch = bot.get_channel(send_channel_id)
    try:
        await ch.send(embed=discord.Embed(title='Bye', description="다음에 다시 만나요.", color=0x00ff00))
        await vc.disconnect()
    except:
        await ch.send(embed=discord.Embed(title='Notice', description="이미 오프라인이에요", color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 재생_URL(ctx, *, url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    ch = bot.get_channel(send_channel_id)
    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ch.send(embed=discord.Embed(title="Now Playing", description="재생\n" + url, color=0x00ff00))
    else:
        await ch.send("노래가 이미 재생되고 있습니다!")
    await ctx.message.delete()


@bot.command()
async def 재생(ctx, *, msg):
    ch = bot.get_channel(send_channel_id)
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ch.send(embed=discord.Embed(title='Notice', description="음성채널에 아무도 없어요.", color=0x00ff00))

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}

        # MODE : local
        # chromedriver_dir = r"D:\chromedriver.exe"
        # driver = webdriver.Chrome(chromedriver_dir, options=options)
        #

        # MODE : server
        driver = load_chrome_driver()
        #

        if "라이브" in msg:
            driver.get("https://www.youtube.com/results?search_query=" + msg)
        else:
            driver.get("https://www.youtube.com/results?search_query=" + msg + "+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com' + musicurl

        driver.quit()
        musicnow.insert(0, entireText)

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ch.send(embed=discord.Embed(title="Now playing", description=musicnow[0], color=0x00ff00))
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ch.send(embed=discord.Embed(title='Add list', description=result + "\n재생목록에 추가 완료", color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 일시정지(ctx):
    ch = bot.get_channel(send_channel_id)
    if vc.is_playing():
        vc.pause()
        await ch.send(embed=discord.Embed(title="Pause", description=musicnow[0] + "\n일시정지 했습니다.", color=0x00ff00))
    else:
        await ch.send("지금 노래가 재생되지 않네요.")
    await ctx.message.delete()


@bot.command()
async def 다시재생(ctx):
    ch = bot.get_channel(send_channel_id)
    try:
        vc.resume()
        await ch.send(embed=discord.Embed(title="Resume", description=musicnow[0] + "\n다시 재생할게요.", color=0x00ff00))
    except:
        await ch.send("지금 노래가 재생되지 않네요.")
    await ctx.message.delete()


@bot.command()
async def 정지(ctx):
    ch = bot.get_channel(send_channel_id)
    if vc.is_playing():
        vc.stop()
        await ch.send(embed=discord.Embed(title="Stop", description=musicnow[0] + "\n정지했습니다.", color=0x00ff00))
    else:
        await ch.send("지금 노래가 재생되지 않네요.")
    await ctx.message.delete()


@bot.command()
async def 재생중(ctx):
    ch = bot.get_channel(send_channel_id)
    if not vc.is_playing():
        await ch.send("재생 중인 노래가 없습니다.")
    else:
        await ch.send(
            embed=discord.Embed(title="Now playing", description="현재 재생 중인 곡은\n" + musicnow[0] + "\n입니다.",
                                color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 멜론(ctx):
    ch = bot.get_channel(send_channel_id)
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ch.send(embed=discord.Embed(title='Notice', description="Nobody in any channel", color=0x00ff00))

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}

        # MODE : local
        # chromedriver_dir = r"D:\chromedriver.exe"
        # driver = webdriver.Chrome(chromedriver_dir, options=options)
        #

        # MODE : server
        driver = load_chrome_driver()
        #

        driver.get("https://www.youtube.com/results?search_query=멜론차트")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com' + musicurl

        driver.quit()
        musicnow.insert(0, entireText)

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ch.send(
            embed=discord.Embed(title="Newest Melon Top 100", description=entireText, color=0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        user.append("멜론")
        result, URLTEST = title("멜론")
        song_queue.append(URLTEST)
        await ch.send(embed=discord.Embed(title='Add list', description=result + "\n재생목록에 추가 완료", color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 추가(ctx, *, msg):
    ch = bot.get_channel(send_channel_id)
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ch.send(embed=discord.Embed(title='Add list', description=result + "\n재생목록에 추가 완료", color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        tmpTitle = musictitle[int(number) - 1]
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number) - 1]
        del musicnow[int(number) - 1 + ex]

        await ch.send(
            embed=discord.Embed(title='Remove list', description=number + "번 : " + tmpTitle + " 제거 완료", color=0x00ff00))
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없습니다.")
        else:
            if len(list) < int(number):
                await ctx.send("숫자가 리스트의 범위를 벗어났습니다.")
            else:
                await ctx.send("숫자를 입력해주세요.")
    await ctx.message.delete()


@bot.command()
async def 제거(ctx, *, number):
    ch = bot.get_channel(send_channel_id)
    try:
        ex = len(musicnow) - len(user)
        tmpTitle = musictitle[int(number) - 1]
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number) - 1]
        del musicnow[int(number) - 1 + ex]

        await ch.send(
            embed=discord.Embed(title='Remove list', description=number + "번 : " + tmpTitle + " 제거 완료", color=0x00ff00))
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없습니다.")
        else:
            if len(list) < int(number):
                await ctx.send("숫자가 리스트의 범위를 벗어났습니다.")
            else:
                await ctx.send("숫자를 입력해주세요.")
    await ctx.message.delete()


@bot.command()
async def 목록(ctx):
    ch = bot.get_channel(send_channel_id)
    if len(musictitle) == 0:
        await ctx.send("리스트에 등록된 노래가 없습니다.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])

        await ch.send(embed=discord.Embed(title="List", description=Text.strip(), color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 리스트(ctx):
    if len(musictitle) == 0:
        await ctx.send("리스트에 등록된 노래가 없습니다.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])

        await ctx.send(embed=discord.Embed(title="List", description=Text.strip(), color=0x00ff00))
    await ctx.message.delete()


@bot.command()
async def 초기화(ctx):
    ch = bot.get_channel(send_channel_id)
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
        await ch.send(
            embed=discord.Embed(title="Reset list", description="""리스트가 정상적으로 초기화되었습니다.""", color=0x00ff00))
    except:
        await ctx.send("리스트에 등록된 노래가 없습니다.")
    await ctx.message.delete()


@bot.command()
async def 번호재생(ctx):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if len(user) == 0:
        await ctx.send("리스트에 등록된 노래가 없습니다")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생 중 입니다.")
    await ctx.message.delete()


@bot.command()
async def 스킵(ctx):
    ch = bot.get_channel(send_channel_id)
    if len(user) > 1:
        if vc.is_playing():
            vc.stop()
            global number
            number = 0
            await ch.send(embed=discord.Embed(title="Skip", description="Skipped", color=0x00ff00))
        else:
            await ctx.send("스킵_예외오류")
    else:
        await ctx.send("다음 곡이 없습니다.")
    await ctx.message.delete()


@bot.command()
async def 도움말(ctx):
    ch = bot.get_channel(send_channel_id)
    await ch.send(embed=discord.Embed(title='도움말', description="""
        \n!도움말 -> 뮤직봇의 모든 명령어를 볼 수 있습니다.
        \n!들 -> 뮤직봇을 자신이 속한 채널로 부릅니다.
        \n!나 -> 뮤직봇을 자신이 속한 채널에서 내보냅니다.
        \n!재생_URL 노래링크 -> 유튜브 URL을 입력하면 뮤직봇이 노래를 틀어줍니다.
        (목록재생에서는 사용할 수 없습니다.)
        \n!재생 노래제목 -> 노래를 검색해 틀어줍니다.
        \n!정지 -> 현재 재생중인 노래를 끕니다.
        !일시정지 -> 현재 재생중인 노래를 일시정지합니다.
        !다시재생 -> 일시정지한 노래를 다시 재생합니다.
        \n!재생중 -> 현재 재생되고 있는 노래의 제목을 알려줍니다.
        \n!멜론 -> 최신 멜론차트를 재생합니다.
        \n!목록 or !리스트 -> 이어서 재생할 노래목록을 보여줍니다.
        !번호재생 번호 -> 목록에 추가된 노래를 재생합니다.
        !초기화 -> 목록에 추가된 모든 노래를 지웁니다.
        !스킵 -> 현재 노래를 종료하고 다음 노래를 재생합니다.
        \n!추가 노래제목 -> 노래를 대기열에 추가합니다.
        !삭제 or !제거 숫자 -> 대기열에서 입력한 숫자에 해당하는 노래를 지웁니다.""", color=0x8b00ff))
    await ctx.message.delete()


bot.run('OTI2Mzg4MTA5MjgzODUyMzE4.Yc68KA.qA3qoRViD234lyEWDSOwJhhxMq4')
