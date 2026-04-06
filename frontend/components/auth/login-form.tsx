"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { IconBrandGithub, IconBrandGoogle, IconMail, IconLock, IconUser } from "@tabler/icons-react";
import { cn } from "@/lib/utils";

interface LoginFormProps {
  className?: string;
  onSuccess?: () => void;
}

export function LoginForm({ className, onSuccess }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    
    const formData = new FormData(e.currentTarget);
    const identifier = formData.get("identifier") as string;
    const password = formData.get("password") as string;
    
    try {
      // TODO: 调用后端登录API
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
      // TODO: 调用后端注册API
      console.log("注册信息:", { username, email, password });
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 切换到登录标签页
      setActiveTab("login");
      alert("注册成功！请登录");
    } catch (error) {
      console.error("注册失败:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: "github" | "google") => {
    setIsLoading(true);
    try {
      console.log(`使用${provider}登录`);
      // TODO: 实现社交登录
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error("社交登录失败:", error);
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
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as "login" | "register")}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="login">登录</TabsTrigger>
            <TabsTrigger value="register">注册</TabsTrigger>
          </TabsList>
          
          <TabsContent value="login">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-identifier">用户名或邮箱</Label>
                <div className="relative">
                  <IconMail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="login-identifier"
                    name="identifier"
                    placeholder="username@example.com"
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="login-password">密码</Label>
                  <a
                    href="#"
                    className="text-sm text-primary hover:underline"
                    onClick={(e) => e.preventDefault()}
                  >
                    忘记密码？
                  </a>
                </div>
                <div className="relative">
                  <IconLock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="login-password"
                    name="password"
                    type="password"
                    placeholder="••••••••"
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "登录中..." : "登录"}
              </Button>
            </form>
          </TabsContent>
          
          <TabsContent value="register">
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="register-username">用户名</Label>
                <div className="relative">
                  <IconUser className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="register-username"
                    name="username"
                    placeholder="john_doe"
                    className="pl-10"
                    required
                    minLength={3}
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="register-email">邮箱</Label>
                <div className="relative">
                  <IconMail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="register-email"
                    name="email"
                    type="email"
                    placeholder="john@example.com"
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="register-password">密码</Label>
                <div className="relative">
                  <IconLock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="register-password"
                    name="password"
                    type="password"
                    placeholder="••••••••"
                    className="pl-10"
                    required
                    minLength={6}
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="register-confirm-password">确认密码</Label>
                <div className="relative">
                  <IconLock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="register-confirm-password"
                    name="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    className="pl-10"
                    required
                    minLength={6}
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "注册中..." : "注册"}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
        
        <div className="relative my-6">
          <Separator />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="bg-background px-2 text-sm text-muted-foreground">
              或使用社交账号
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <Button
            variant="outline"
            type="button"
            disabled={isLoading}
            onClick={() => handleSocialLogin("github")}
            className="w-full"
          >
            <IconBrandGithub className="mr-2 h-4 w-4" />
            GitHub
          </Button>
          <Button
            variant="outline"
            type="button"
            disabled={isLoading}
            onClick={() => handleSocialLogin("google")}
            className="w-full"
          >
            <IconBrandGoogle className="mr-2 h-4 w-4" />
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