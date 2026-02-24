import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, LogIn, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

const loginSchema = z.object({
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
});

const LoginForm = () => {
    const navigate = useNavigate();
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data) => {
        try {
            // Simulate API call
            await new Promise((resolve) => setTimeout(resolve, 1500));
            console.log("Login data:", data);
            toast.success("Welcome back! Login successful.");
            navigate("/");
        } catch (error) {
            toast.error("Invalid credentials. Please try again.");
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
                <label className="text-sm font-medium text-foreground/80 ml-1">Email Address</label>
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        {...register("email")}
                        type="email"
                        placeholder="name@example.com"
                        className={`block w-full pl-11 pr-4 py-3.5 bg-background border rounded-1.5xl transition-all outline-none text-foreground ${errors.email
                            ? "border-destructive focus:ring-4 focus:ring-destructive/10"
                            : "border-border focus:border-primary focus:ring-4 focus:ring-primary/10"
                            }`}
                    />
                </div>
                {errors.email && (
                    <p className="mt-1 text-sm text-destructive font-medium ml-1">
                        {errors.email.message}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <label className="text-sm font-medium text-foreground/80 ml-1">Password</label>
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        {...register("password")}
                        type="password"
                        placeholder="••••••••"
                        className={`block w-full pl-11 pr-4 py-3.5 bg-background border rounded-1.5xl transition-all outline-none text-foreground ${errors.password
                            ? "border-destructive focus:ring-4 focus:ring-destructive/10"
                            : "border-border focus:border-primary focus:ring-4 focus:ring-primary/10"
                            }`}
                    />
                </div>
                {errors.password && (
                    <p className="mt-1 text-sm text-destructive font-medium ml-1">
                        {errors.password.message}
                    </p>
                )}
            </div>

            <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 py-4 px-4 bg-primary text-white rounded-1.5xl font-bold text-lg shadow-lg shadow-primary/30 hover:bg-primary/90 hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
            >
                {isSubmitting ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                    <>
                        <LogIn className="w-5 h-5" />
                        Login
                    </>
                )}
            </button>

            <div className="text-center pt-2">
                <p className="text-muted-foreground font-medium">
                    Don't have an account?{" "}
                    <Link
                        to="/register"
                        className="text-primary font-bold hover:underline underline-offset-4"
                    >
                        Sign up
                    </Link>
                </p>
            </div>
        </form>
    );
};

export default LoginForm;
