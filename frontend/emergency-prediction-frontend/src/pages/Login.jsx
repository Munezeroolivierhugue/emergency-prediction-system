import React from "react";
import AuthLayout from "../components/AuthLayout";
import LoginForm from "../components/LoginForm";

const Login = () => {
    return (
        <AuthLayout
            title="Welcome Back"
            subtitle="Log in to your command center to continue"
        >
            <LoginForm />
        </AuthLayout>
    );
};

export default Login;
