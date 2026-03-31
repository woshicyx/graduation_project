export type Movie = {
  id: string;
  title: string;
  director: string;
  genres: string[];
  rating: number;
  boxOffice: number;
  releaseDate: string;
  posterUrl: string;
  popularity: number;
  synopsis: string;
};

export const dailyPick: Movie = {
  id: "1",
  title: "星际穿越 Interstellar",
  director: "Christopher Nolan",
  genres: ["科幻", "剧情"],
  rating: 9.3,
  boxOffice: 675000000,
  releaseDate: "2014-11-07",
  posterUrl:
    "https://image.tmdb.org/t/p/original/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
  popularity: 98.5,
  synopsis:
    "在不远的未来，地球资源枯竭，一支探索小队穿越虫洞，寻找人类的新家园，同时面对时间、亲情与命运的极限考验。",
};

export const topBoxOffice: Movie[] = [
  {
    id: "2",
    title: "阿凡达 Avatar",
    director: "James Cameron",
    genres: ["科幻", "冒险"],
    rating: 8.8,
    boxOffice: 2847246203,
    releaseDate: "2009-12-18",
    posterUrl:
      "https://image.tmdb.org/t/p/original/tYfijzolzgoMOtegh1Y7j2Enorg.jpg",
    popularity: 96.0,
    synopsis:
      "人类在潘多拉星球开采珍贵资源，一名残疾士兵被卷入人类与纳美人的冲突之中。",
  },
  {
    id: "3",
    title: "复仇者联盟4：终局之战",
    director: "Anthony Russo, Joe Russo",
    genres: ["动作", "科幻"],
    rating: 8.9,
    boxOffice: 2797501328,
    releaseDate: "2019-04-26",
    posterUrl:
      "https://image.tmdb.org/t/p/original/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
    popularity: 94.1,
    synopsis: "幸存的英雄们集结，试图逆转无限战争带来的毁灭性后果。",
  },
  {
    id: "4",
    title: "阿凡达：水之道",
    director: "James Cameron",
    genres: ["科幻", "冒险"],
    rating: 8.2,
    boxOffice: 2320250281,
    releaseDate: "2022-12-16",
    posterUrl:
      "https://image.tmdb.org/t/p/original/j0qMwsO0x8ZbG1xZg7M8ZEFZCz6.jpg",
    popularity: 89.4,
    synopsis: "杰克与家庭在潘多拉的海洋部落中继续对抗新的威胁。",
  },
  {
    id: "8",
    title: "泰坦尼克号 Titanic",
    director: "James Cameron",
    genres: ["剧情", "爱情"],
    rating: 8.9,
    boxOffice: 2201647264,
    releaseDate: "1997-12-19",
    posterUrl:
      "https://image.tmdb.org/t/p/original/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
    popularity: 91.5,
    synopsis: "穷画家杰克与贵族女露丝在泰坦尼克号上的凄美爱情故事。",
  },
  {
    id: "9",
    title: "星球大战：原力觉醒",
    director: "J.J. Abrams",
    genres: ["科幻", "冒险"],
    rating: 8.0,
    boxOffice: 2068223624,
    releaseDate: "2015-12-18",
    posterUrl:
      "https://image.tmdb.org/t/p/original/wqnLdwVXoBjKibFRR5U3y0aDUhs.jpg",
    popularity: 87.2,
    synopsis: "拾荒者蕾伊与逃兵芬恩卷入抵抗组织与第一秩序的战争。",
  },
  {
    id: "10",
    title: "复仇者联盟3：无限战争",
    director: "Anthony Russo, Joe Russo",
    genres: ["动作", "科幻"],
    rating: 8.8,
    boxOffice: 2048359754,
    releaseDate: "2018-04-27",
    posterUrl:
      "https://image.tmdb.org/t/p/original/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
    popularity: 93.8,
    synopsis: "灭霸收集无限宝石，意图抹除宇宙一半生命，英雄们奋起反抗。",
  },
  {
    id: "11",
    title: "蜘蛛侠：英雄无归",
    director: "Jon Watts",
    genres: ["动作", "科幻"],
    rating: 8.5,
    boxOffice: 1921847111,
    releaseDate: "2021-12-17",
    posterUrl:
      "https://image.tmdb.org/t/p/original/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
    popularity: 90.1,
    synopsis: "蜘蛛侠的身份暴露，他求助奇异博士却引发多元宇宙危机。",
  },
  {
    id: "12",
    title: "侏罗纪世界",
    director: "Colin Trevorrow",
    genres: ["科幻", "冒险"],
    rating: 7.8,
    boxOffice: 1671713208,
    releaseDate: "2015-06-12",
    posterUrl:
      "https://image.tmdb.org/t/p/original/jjBgi2r5cRt36xF6iNUEhzscEcb.jpg",
    popularity: 85.3,
    synopsis: "侏罗纪公园重新开放，但基因改造的恐龙失控引发灾难。",
  },
];

export const topRated: Movie[] = [
  {
    id: "5",
    title: "肖申克的救赎",
    director: "Frank Darabont",
    genres: ["剧情"],
    rating: 9.7,
    boxOffice: 58300000,
    releaseDate: "1994-09-23",
    posterUrl:
      "https://image.tmdb.org/t/p/original/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
    popularity: 92.3,
    synopsis: "银行家安迪因冤案入狱，在绝望之地寻找自由与希望。",
  },
  {
    id: "6",
    title: "霸王别姬",
    director: "陈凯歌",
    genres: ["剧情", "爱情"],
    rating: 9.6,
    boxOffice: 50000000,
    releaseDate: "1993-01-01",
    posterUrl:
      "https://image.tmdb.org/t/p/original/2P5eNS8XcLk9gWkA36TObgGJEfk.jpg",
    popularity: 88.2,
    synopsis: "一段跨越半个世纪的戏曲人生，纠缠在国运、舞台与感情之间。",
  },
  {
    id: "7",
    title: "盗梦空间 Inception",
    director: "Christopher Nolan",
    genres: ["科幻", "悬疑"],
    rating: 9.4,
    boxOffice: 836800000,
    releaseDate: "2010-07-16",
    posterUrl:
      "https://image.tmdb.org/t/p/original/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",
    popularity: 95.0,
    synopsis: "盗梦者柯布带领团队潜入他人潜意识，在梦境层层深入完成几乎不可能的任务。",
  },
  {
    id: "13",
    title: "教父 The Godfather",
    director: "Francis Ford Coppola",
    genres: ["剧情", "犯罪"],
    rating: 9.5,
    boxOffice: 250000000,
    releaseDate: "1972-03-24",
    posterUrl:
      "https://image.tmdb.org/t/p/original/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
    popularity: 91.8,
    synopsis: "黑手党家族首领维托·柯里昂的小儿子迈克尔如何接掌家族事业。",
  },
  {
    id: "14",
    title: "黑暗骑士 The Dark Knight",
    director: "Christopher Nolan",
    genres: ["动作", "犯罪"],
    rating: 9.3,
    boxOffice: 1004558444,
    releaseDate: "2008-07-18",
    posterUrl:
      "https://image.tmdb.org/t/p/original/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    popularity: 94.7,
    synopsis: "蝙蝠侠与小丑在哥谭市的终极对决，探讨秩序与混乱的边界。",
  },
  {
    id: "15",
    title: "十二怒汉 12 Angry Men",
    director: "Sidney Lumet",
    genres: ["剧情"],
    rating: 9.2,
    boxOffice: 2000000,
    releaseDate: "1957-04-10",
    posterUrl:
      "https://image.tmdb.org/t/p/original/ppd84D2i9W8jXmsyInGyihiSyqz.jpg",
    popularity: 86.5,
    synopsis: "陪审团成员在审议谋杀案时，一人坚持无罪引发激烈辩论。",
  },
  {
    id: "16",
    title: "辛德勒的名单 Schindler's List",
    director: "Steven Spielberg",
    genres: ["剧情", "历史"],
    rating: 9.1,
    boxOffice: 321200000,
    releaseDate: "1993-12-15",
    posterUrl:
      "https://image.tmdb.org/t/p/original/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
    popularity: 89.3,
    synopsis: "德国商人辛德勒在二战期间拯救上千犹太人的真实故事。",
  },
  {
    id: "17",
    title: "指环王：王者归来",
    director: "Peter Jackson",
    genres: ["奇幻", "冒险"],
    rating: 9.0,
    boxOffice: 1146030912,
    releaseDate: "2003-12-17",
    posterUrl:
      "https://image.tmdb.org/t/p/original/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg",
    popularity: 93.1,
    synopsis: "弗罗多与山姆接近末日火山，阿拉贡领导中土世界对抗索伦。",
  },
];

