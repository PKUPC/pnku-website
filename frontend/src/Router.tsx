import { Navigate, RouteObject, RouterProvider, createBrowserRouter, useOutlet } from 'react-router-dom';

import GeneralLayout from '@/app/(general)/GeneralLayout.tsx';
import { AboutLayout } from '@/app/(general)/about/AboutLayout.tsx';
import { FaqPage } from '@/app/(general)/about/faq/page.tsx';
import IntroductionPage from '@/app/(general)/about/introduction/page.tsx';
import { ToolsPage } from '@/app/(general)/about/tools/page.tsx';
import { BoardLayout } from '@/app/(general)/boards/BoardLayout.tsx';
import { BoardPage } from '@/app/(general)/boards/page.tsx';
import { InfoLayout } from '@/app/(general)/info/InfoLayout.tsx';
import { AnnouncementPage } from '@/app/(general)/info/announcements/page.tsx';
import { MessagePage } from '@/app/(general)/info/message/page.tsx';
import { SchedulePage } from '@/app/(general)/info/schedule/page.tsx';
import { LoginErrorPage } from '@/app/(general)/login/error/page.tsx';
import { LoginPage } from '@/app/(general)/login/page.tsx';
import { PlazaPage } from '@/app/(general)/plaza/page.tsx';
import { PuzzleLayout } from '@/app/(general)/puzzle/PuzzleLayout.tsx';
import { PuzzlePage } from '@/app/(general)/puzzle/page.tsx';
import { SettingPage } from '@/app/(general)/setting/page.tsx';
import { StoryPage } from '@/app/(general)/story/page.tsx';
import { TeamLayout } from '@/app/(general)/team/TeamLayout.tsx';
import { CurrencyHistoryPage } from '@/app/(general)/team/currency-history/page.tsx';
import { PuzzleStatisticsPage } from '@/app/(general)/team/puzzle-statistics/page.tsx';
import { SubmissionHistoryPage } from '@/app/(general)/team/submission-history/page.tsx';
import { TicketDetailPage } from '@/app/(general)/ticket-detail/page.tsx';
import { ToolsLayout } from '@/app/(general)/tools/ToolsLayout.tsx';
import { UploadImagePage } from '@/app/(general)/tools/upload-image/page.tsx';
import UserLayout from '@/app/(general)/user/UserLayout.tsx';
import { UserProfilePage } from '@/app/(general)/user/profile/page.tsx';
import { UserSecurityPage } from '@/app/(general)/user/security/page.tsx';
import { UserTeamPage } from '@/app/(general)/user/team/page.tsx';
import NotFound from '@/app/NotFound.tsx';
import { RouterErrorBoundary } from '@/app/RouterErrorBoundary.tsx';
import { AreaPage } from '@/app/area/page.tsx';
import { HomePage } from '@/app/home/page.tsx';
import { PuzzleListPage } from '@/app/puzzle-list/page.tsx';
import { StoryListPage } from '@/app/story-list/page.tsx';
import { Header } from '@/components/DaisyUI/Header.tsx';

function AppLayout() {
    console.debug('Rendering AppLayout');
    const outlet = useOutlet();

    return (
        <>
            <Header />
            {outlet}
        </>
    );
}

const routes: RouteObject[] = [
    {
        element: <AppLayout />,
        errorElement: <RouterErrorBoundary />,
        children: [
            { path: '/', element: <Navigate to={'/home'} replace={true} /> },
            { path: '/home', element: <HomePage /> },
            { path: '/area', element: <AreaPage /> },
            { path: '/puzzle-list', element: <PuzzleListPage /> },
            { path: '/story-list', element: <StoryListPage /> },
            {
                element: <GeneralLayout />,
                children: [
                    { path: '/login', element: <LoginPage /> },
                    { path: '/login/error', element: <LoginErrorPage /> },
                    { path: '/plaza', element: <PlazaPage /> },
                    { path: '/setting', element: <SettingPage /> },
                    {
                        element: <PuzzleLayout />,
                        children: [{ path: '/puzzle', element: <PuzzlePage /> }],
                    },
                    { path: '/story', element: <StoryPage /> },
                    { path: '/ticket-detail', element: <TicketDetailPage /> },
                    {
                        path: '/boards',
                        element: <BoardLayout />,
                        children: [{ element: <BoardPage />, index: true }],
                    },
                    {
                        path: '/tools',
                        element: <ToolsLayout />,
                        children: [
                            { index: true, element: <Navigate to="/tools/upload-image" /> },
                            { path: '/tools/upload-image', element: <UploadImagePage /> },
                        ],
                    },
                    {
                        path: '/about',
                        element: <AboutLayout />,
                        children: [
                            { index: true, element: <Navigate to="/about/introduction" /> },
                            { path: '/about/introduction', element: <IntroductionPage /> },
                            { path: '/about/faq', element: <FaqPage /> },
                            { path: '/about/tools', element: <ToolsPage /> },
                        ],
                    },
                    {
                        path: '/info',
                        element: <InfoLayout />,
                        children: [
                            { index: true, element: <Navigate to="/info/announcements" /> },
                            { path: '/info/message', element: <MessagePage /> },
                            { path: '/info/announcements', element: <AnnouncementPage /> },
                            { path: '/info/schedule', element: <SchedulePage /> },
                        ],
                    },
                    {
                        path: '/user',
                        element: <UserLayout />,
                        children: [
                            { index: true, element: <Navigate to="/user/profile" /> },
                            { path: '/user/profile', element: <UserProfilePage /> },
                            { path: '/user/team', element: <UserTeamPage /> },
                            { path: '/user/security', element: <UserSecurityPage /> },
                        ],
                    },
                    {
                        path: '/team',
                        element: <TeamLayout />,
                        children: [
                            { index: true, element: <Navigate to="/about/introduction" /> },
                            { path: '/team/currency-history', element: <CurrencyHistoryPage /> },
                            { path: '/team/puzzle-statistics', element: <PuzzleStatisticsPage /> },
                            { path: '/team/submission-history', element: <SubmissionHistoryPage /> },
                        ],
                    },
                    {
                        path: '/staff',
                        async lazy() {
                            const { StaffLayout } = await import('@/app/(general)/staff/StaffLayout.tsx');
                            return { Component: StaffLayout };
                        },
                        children: [
                            { index: true, element: <Navigate to="/staff/teams" /> },
                            {
                                async lazy() {
                                    const { StaffMenuLayout } = await import('@/app/(general)/staff/StaffLayout.tsx');
                                    return { Component: StaffMenuLayout };
                                },
                                children: [
                                    {
                                        path: '/staff/teams',
                                        async lazy() {
                                            const { StaffTeamPage } = await import(
                                                '@/app/(general)/staff/StaffLayout.tsx'
                                            );
                                            return { Component: StaffTeamPage };
                                        },
                                    },
                                    {
                                        path: '/staff/tickets',
                                        async lazy() {
                                            const { StaffTicketPage } = await import(
                                                '@/app/(general)/staff/StaffLayout.tsx'
                                            );
                                            return { Component: StaffTicketPage };
                                        },
                                    },
                                    {
                                        path: '/staff/submissions',
                                        async lazy() {
                                            const { StaffSubmissionPage } = await import(
                                                '@/app/(general)/staff/StaffLayout.tsx'
                                            );
                                            return { Component: StaffSubmissionPage };
                                        },
                                    },
                                ],
                            },
                            {
                                async lazy() {
                                    const { StaffDetailLayout } = await import('@/app/(general)/staff/StaffLayout.tsx');
                                    return { Component: StaffDetailLayout };
                                },
                                children: [
                                    {
                                        path: '/staff/message',
                                        async lazy() {
                                            const { StaffMessagePage } = await import(
                                                '@/app/(general)/staff/StaffLayout.tsx'
                                            );
                                            return { Component: StaffMessagePage };
                                        },
                                    },
                                    {
                                        path: '/staff/team-detail',
                                        async lazy() {
                                            const { StaffTeamDetailPage } = await import(
                                                '@/app/(general)/staff/StaffLayout.tsx'
                                            );
                                            return { Component: StaffTeamDetailPage };
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            { path: '*', element: <NotFound /> },
        ],
    },
];

export function AppRouter() {
    return <RouterProvider router={createBrowserRouter(routes)} />;
}
