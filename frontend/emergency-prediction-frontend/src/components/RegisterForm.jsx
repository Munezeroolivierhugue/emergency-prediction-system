import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useNavigate, Link } from "react-router-dom";
import { Mail, Lock, User, UserPlus, Loader2, ShieldCheck } from "lucide-react";
import toast from "react-hot-toast";

import { authService } from "../utils/api";

const registerSchema = z
    .object({
        name: z.string().min(2, "Name must be at least 2 characters"),
        email: z.string().email("Please enter a valid email address"),
        password: z.string().min(6, "Password must be at least 6 characters"),
        confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Passwords don't match",
        path: ["confirmPassword"],
    });

const RegisterForm = () => {
    const navigate = useNavigate();
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data) => {
        try {
            await authService.register({
                name: data.name,
                email: data.email,
                password: data.password
            });

            toast.success("Account created successfully! Please log in.");
            navigate("/login");
        } catch (error) {
            console.error("Registration error:", error);
            const message = error.response?.data?.detail || "Failed to create account. Try again.";
            toast.error(message);
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 ml-1">Full Name</label>
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        {...register("name")}
                        type="text"
                        placeholder="John Doe"
                        className={`block w-full pl-11 pr-4 py-3 bg-background border rounded-1.5xl transition-all outline-none text-foreground ${errors.name
                            ? "border-destructive focus:ring-4 focus:ring-destructive/10"
                            : "border-border focus:border-primary focus:ring-4 focus:ring-primary/10"
                            }`}
                    />
                </div>
                {errors.name && (
                    <p className="mt-1 text-sm text-destructive font-medium ml-1">
                        {errors.name.message}
                    </p>
                )}
            </div>

            <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 ml-1">Email Address</label>
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        {...register("email")}
                        type="email"
                        placeholder="name@example.com"
                        className={`block w-full pl-11 pr-4 py-3 bg-background border rounded-1.5xl transition-all outline-none text-foreground ${errors.email
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

            <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 ml-1">Password</label>
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        {...register("password")}
                        type="password"
                        placeholder="••••••••"
                        className={`block w-full pl-11 pr-4 py-3 bg-background border rounded-1.5xl transition-all outline-none text-foreground ${errors.password
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

            <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 ml-1">Confirm Password</label>
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <ShieldCheck className="h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        {...register("confirmPassword")}
                        type="password"
                        placeholder="••••••••"
                        className={`block w-full pl-11 pr-4 py-3 bg-background border rounded-1.5xl transition-all outline-none text-foreground ${errors.confirmPassword
                            ? "border-destructive focus:ring-4 focus:ring-destructive/10"
                            : "border-border focus:border-primary focus:ring-4 focus:ring-primary/10"
                            }`}
                    />
                </div>
                {errors.confirmPassword && (
                    <p className="mt-1 text-sm text-destructive font-medium ml-1">
                        {errors.confirmPassword.message}
                    </p>
                )}
            </div>

            <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 py-4 px-4 bg-primary text-white rounded-1.5xl font-bold text-lg shadow-lg shadow-primary/30 hover:bg-primary/90 hover:-tranneutral-y-0.5 active:tranneutral-y-0 transition-all disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none mt-4"
            >
                {isSubmitting ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                    <>
                        <UserPlus className="w-5 h-5" />
                        Create Account
                    </>
                )}
            </button>

            <div className="text-center pt-2">
                <p className="text-muted-foreground font-medium text-sm">
                    Already have an account?{" "}
                    <Link
                        to="/login"
                        className="text-primary font-bold hover:underline underline-offset-4"
                    >
                        Log in
                    </Link>
                </p>
            </div>
        </form>
    );
};

export default RegisterForm;
