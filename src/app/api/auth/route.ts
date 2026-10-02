import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const { password } = await request.json()
    const correctPassword = process.env.DASHBOARD_PASSWORD || 'defaultpassword'

    if (password === correctPassword) {
      const response = NextResponse.json({ success: true })
      
      // Set cookie for 30 days
      response.cookies.set({
        name: 'auth_token',
        value: 'authenticated',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 30, // 30 days
        path: '/',
      })
      
      return response
    }

    return NextResponse.json({ success: false, error: 'Incorrect password' }, { status: 401 })
  } catch (error) {
    return NextResponse.json({ success: false, error: 'Bad request' }, { status: 400 })
  }
}
