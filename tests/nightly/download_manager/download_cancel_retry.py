# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
from moziris.api.mouse import mouse
from targets.nightly.firefox_ui.download_manager import DownloadManager
from targets.nightly.firefox_ui.helpers.download_manager_utils import *
from targets.nightly.fx_testcase import *


class Test(FirefoxTest):
    @pytest.mark.details(
        description="A download can be cancelled and retried.",
        locale=["en-US"],
        test_case_id="99470",
        test_suite_id="1827",
        profile=Profiles.BRAND_NEW,
        preferences={
            "browser.download.autohideButton": False,
            "browser.download.dir": PathManager.get_downloads_dir(),
            "browser.download.folderList": 2,
            "browser.download.panel.shown": True,
            "browser.download.useDownloadDir": True,
            "browser.warnOnQuit": False,
        },
    )
    def run(self, firefox):
        file_to_download = DownloadFiles.VERY_LARGE_FILE_1GB
        download_cancelled_pattern = DownloadManager.DownloadState.CANCELLED.similar(0.6)
        region = Screen.TOP_THIRD

        navigate('https://irisfirefoxtestfiles.netlify.com')

        expected = exists(DownloadFiles.VERY_LARGE_FILE_1GB, FirefoxSettings.SITE_LOAD_TIMEOUT)
        assert expected is True, "Test page is displayed."

        select_throttling(NetworkOption.GOOD_3G)

        download_file(file_to_download, DownloadFiles.OK)

        expected = region.exists(NavBar.DOWNLOADS_BUTTON, 10)
        assert expected is True, "Downloads button is displayed."
        region.click(NavBar.DOWNLOADS_BUTTON)
        time.sleep(Settings.DEFAULT_UI_DELAY_LONG)

        expected = region.exists(DownloadManager.DownloadsPanel.DOWNLOAD_CANCEL, 10)
        assert expected is True, "Cancel button is displayed."
        time.sleep(Settings.DEFAULT_UI_DELAY)

        region.click(DownloadManager.DownloadsPanel.DOWNLOAD_CANCEL)
        if OSHelper.get_os() != OSPlatform.LINUX:
            expected = exists(DownloadManager.DownloadState.RETRY_DOWNLOAD, 15)
            assert expected is True, "Retry download message is displayed."

        reset_mouse()
        expected = region.exists(download_cancelled_pattern, 15)
        assert expected is True, "Download was cancelled."

        expected = region.exists(DownloadManager.DownloadsPanel.DOWNLOAD_RETRY, 10)
        assert expected is True, "Retry button is displayed."
        time.sleep(Settings.DEFAULT_UI_DELAY_LONG)

        region.click(DownloadManager.DownloadsPanel.DOWNLOAD_RETRY)
        reset_mouse()
        expected = region.exists(DownloadManager.DownloadState.PROGRESS, 10)
        assert expected is True, "Download was restarted."
        assert expected is True, "Retry button is displayed."
        time.sleep(Settings.DEFAULT_UI_DELAY)

        # Cancel 'in progress' download.
        expected = region.exists(DownloadManager.DownloadsPanel.DOWNLOAD_CANCEL, 10)
        assert expected is True, "Cancel button is displayed."
        time.sleep(Settings.DEFAULT_UI_DELAY)

        region.click(DownloadManager.DownloadsPanel.DOWNLOAD_CANCEL)
        time.sleep(Settings.DEFAULT_UI_DELAY)
        type(Key.ESC)

    def teardown(self):
        downloads_cleanup()
