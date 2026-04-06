"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Menu, User, Heart, History, Settings, LogOut, LogIn, UserPlus, Home, Film, Trophy, Info } from "lucide-react";
import { useUser } from "./user-auth-context";

export function UserNavigation() {
  const { user, isLoading, logout } = useUser();
  const [isSheetOpen, setIsSheetOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setIsSheetOpen(false);
  };

  if (isLoading) {
    return (
      <div className="rounded-full border border-slate-700/60 bg-slate-800/40 px-4 py-2 text-sm text-slate-300">
        加载中...
      </div>
    );
  }

  // 移动端菜单内容
  const mobileMenu = (
    <div className="flex flex-col space-y-4 py-4">
      <div className="flex items-center gap-3 px-4 py-2">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
        <h2 className="text-lg font-semibold text-white">
          Movie<span className="text-emerald-400">AI</span>
        </h2>
      </div>
      
      <div className="space-y-1">
        <Link href="/" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">
          <Home className="h-4 w-4" />
          首页
        </Link>
        <Link href="/movies" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">
          <Film className="h-4 w-4" />
          电影库
        </Link>
        <Link href="/ranking" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">
          <Trophy className="h-4 w-4" />
          排行榜
        </Link>
        <Link href="/about" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">
          <Info className="h-4 w-4" />
          关于
        </Link>
      </div>

      <div className="border-t border-slate-800 pt-4">
        {user ? (
          <>
            <div className="flex items-center gap-3 px-4 py-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src={user.avatar_url} alt={user.display_name || user.username} />
                <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
                  {user.display_name?.charAt(0) || user.username.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user.display_name || user.username}</p>
                <p className="text-xs text-slate-400 truncate">{user.email}</p>
              </div>
            </div>
            
            <div className="space-y-1">
              <Link href="/profile" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors" onClick={() => setIsSheetOpen(false)}>
                <User className="h-4 w-4" />
                个人中心
              </Link>
              <Link href="/profile/favorites" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors" onClick={() => setIsSheetOpen(false)}>
                <Heart className="h-4 w-4" />
                我的收藏
              </Link>
              <Link href="/profile/history" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors" onClick={() => setIsSheetOpen(false)}>
                <History className="h-4 w-4" />
                浏览历史
              </Link>
              <Link href="/profile/settings" className="flex items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors" onClick={() => setIsSheetOpen(false)}>
                <Settings className="h-4 w-4" />
                账户设置
              </Link>
              <button onClick={handleLogout} className="flex w-full items-center gap-3 px-4 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">
                <LogOut className="h-4 w-4" />
                退出登录
              </button>
            </div>
          </>
        ) : (
          <div className="space-y-2 px-4">
            <Link href="/auth/login" className="block">
              <Button className="w-full" onClick={() => setIsSheetOpen(false)}>
                <LogIn className="mr-2 h-4 w-4" />
                登录
              </Button>
            </Link>
            <Link href="/auth/register" className="block">
              <Button variant="outline" className="w-full border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white" onClick={() => setIsSheetOpen(false)}>
                <UserPlus className="mr-2 h-4 w-4" />
                注册
              </Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* 桌面端导航 */}
      <div className="hidden items-center gap-6 text-sm text-slate-300 sm:flex">
        <Link href="/" className="transition-colors hover:text-white">
          首页
        </Link>
        <Link href="/movies" className="transition-colors hover:text-white">
          电影库
        </Link>
        <Link href="/ranking" className="transition-colors hover:text-white">
          排行榜
        </Link>
        <Link href="/about" className="transition-colors hover:text-white">
          关于
        </Link>
      </div>

      {/* 用户相关操作 */}
      <div className="hidden sm:flex items-center gap-2">
        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full p-0">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={user.avatar_url} alt={user.display_name || user.username} />
                  <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
                    {user.display_name?.charAt(0) || user.username.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-slate-900 border-slate-800 text-slate-300">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none text-white">{user.display_name || user.username}</p>
                  <p className="text-xs leading-none text-slate-400 truncate">{user.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-slate-800" />
              <DropdownMenuItem asChild className="hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white cursor-pointer">
                <Link href="/profile">
                  <User className="mr-2 h-4 w-4" />
                  个人中心
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white cursor-pointer">
                <Link href="/profile/favorites">
                  <Heart className="mr-2 h-4 w-4" />
                  我的收藏
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white cursor-pointer">
                <Link href="/profile/history">
                  <History className="mr-2 h-4 w-4" />
                  浏览历史
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white cursor-pointer">
                <Link href="/profile/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  账户设置
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-slate-800" />
              <DropdownMenuItem onClick={handleLogout} className="hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white cursor-pointer text-red-400 hover:text-red-300">
                <LogOut className="mr-2 h-4 w-4" />
                退出登录
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className="flex items-center gap-2">
            <Link href="/auth/login">
              <Button variant="ghost" size="sm" className="border border-slate-700/60 bg-slate-800/40 hover:bg-slate-700/60 hover:text-white text-slate-300">
                登录
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button size="sm" className="bg-gradient-to-br from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white">
                注册
              </Button>
            </Link>
          </div>
        )}
      </div>

      {/* 移动端菜单按钮 */}
      <div className="sm:hidden">
        <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full border border-slate-700/60 bg-slate-800/40 text-slate-300 hover:bg-slate-700/60 hover:text-white">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-[300px] bg-slate-950 border-slate-800 p-0">
            {mobileMenu}
          </SheetContent>
        </Sheet>
      </div>
    </>
  );
}