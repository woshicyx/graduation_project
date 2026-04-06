"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface LoginFormProps {
  className?: string;
  onSuccess?: () => void;
}

export function LoginFormSimple({ className, onSuccess }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    
    const formData = new FormData(e.currentTarget);
    const identifier = formData.get("identifier") as string;
    const password = formData.get("password") as string;
    
    try {
      console.log("登录信息:", { identifier, password });
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error("登录失败:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    
    const formData = new FormData(e.currentTarget);
    const username = formData.get("username") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirmPassword") as string;
    
    if (password !== confirmPassword) {
      alert("密码不匹配");
      setIsLoading(false);
      return;
    }
    
    try {
      console.log("注册信息:", { username, email, password });
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setActiveTab("login");
      alert("注册成功！请登录");
    } catch (error) {
      console.error("注册失败:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className={cn("w-full max-w-md mx-auto", className)}>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center">
          {activeTab === "login" ? "欢迎回来" : "创建账户"}
        </CardTitle>
        <CardDescription className="text-center">
          {activeTab === "login" 
            ? "输入您的凭据以访问您的账户" 
            : "填写以下信息以创建新账户"}
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="flex space-x-2 mb-6">
          <Button
            variant={activeTab === "login" ? "default" : "outline"}
            onClick={() => setActiveTab("login")}
            className="flex-1"
          >
            登录
          </Button>
          <Button
            variant={activeTab === "register" ? "default" : "outline"}
            onClick={() => setActiveTab("register")}
            className="flex-1"
          >
            注册
          </Button>
        </div>
        
        {activeTab === "login" ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="login-identifier" className="text-sm font-medium">
                用户名或邮箱
              </label>
              <Input
                id="login-identifier"
                name="identifier"
                placeholder="username@example.com"
                required
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="login-password" className="text-sm font-medium">
                  密码
                </label>
                <a
                  href="#"
                  className="text-sm text-primary hover:underline"
                  onClick={(e) => e.preventDefault()}
                >
                  忘记密码？
                </a>
              </div>
              <Input
                id="login-password"
                name="password"
                type="password"
                placeholder="••••••••"
                required
                disabled={isLoading}
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "登录中..." : "登录"}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="register-username" className="text-sm font-medium">
                用户名
              </label>
              <Input
                id="register-username"
                name="username"
                placeholder="john_doe"
                required
                minLength={3}
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="register-email" className="text-sm font-medium">
                邮箱
              </label>
              <Input
                id="register-email"
                name="email"
                type="email"
                placeholder="john@example.com"
                required
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="register-password" className="text-sm font-medium">
                密码
              </label>
              <Input
                id="register-password"
                name="password"
                type="password"
                placeholder="••••••••"
                required
                minLength={6}
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="register-confirm-password" className="text-sm font-medium">
                确认密码
              </label>
              <Input
                id="register-confirm-password"
                name="confirmPassword"
                type="password"
                placeholder="••••••••"
                required
                minLength={6}
                disabled={isLoading}
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "注册中..." : "注册"}
            </Button>
          </form>
        )}
        
        <div className="my-6 text-center text-sm text-muted-foreground">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-background px-2">或使用社交账号</span>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <Button
            variant="outline"
            type="button"
            disabled={isLoading}
            onClick={() => console.log("GitHub登录")}
            className="w-full"
          >
            GitHub
          </Button>
          <Button
            variant="outline"
            type="button"
            disabled={isLoading}
            onClick={() => console.log("Google登录")}
            className="w-full"
          >
            Google
          </Button>
        </div>
      </CardContent>
      
      <CardFooter className="flex flex-col space-y-4">
        <div className="text-center text-sm text-muted-foreground">
          {activeTab === "login" ? (
            <>
              还没有账户？{" "}
              <button
                className="text-primary hover:underline"
                onClick={() => setActiveTab("register")}
              >
                立即注册
              </button>
            </>
          ) : (
            <>
              已有账户？{" "}
              <button
                className="text-primary hover:underline"
                onClick={() => setActiveTab("login")}
              >
                立即登录
              </button>
            </>
          )}
        </div>
        
        <div className="text-center text-xs text-muted-foreground">
          继续使用即表示您同意我们的{" "}
          <a href="#" className="underline hover:text-primary" onClick={(e) => e.preventDefault()}>
            服务条款
          </a>{" "}
          和{" "}
          <a href="#" className="underline hover:text-primary" onClick={(e) => e.preventDefault()}>
            隐私政策
          </a>
        </div>
      </CardFooter>
    </Card>
  );
}