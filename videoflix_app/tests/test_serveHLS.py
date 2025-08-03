import os
import shutil
from django.conf import settings
from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from videoflix_app.api.tasks import generate_hls

User = get_user_model()
@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test_media'))
class ServeHLSTests(APITestCase):

    def setUp(self):       
        """ Sets up the test environment for HLS video streaming tests.
        - Creates a test user and assigns an access token for authentication.
        - Initializes movie ID and resolution for the test video.
        - Sets up the test media root directory and output folder for video segments.
        - Checks for the existence of a sample video file and generates HLS segments. """

        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        refresh = RefreshToken.for_user(self.user)        
        self.client.cookies['access_token'] = str(refresh.access_token)
        
        self.movie_id = 1
        self.resolution = '480p'        
        self.test_media_root = settings.MEDIA_ROOT
        self.output_folder = os.path.join(self.test_media_root, 'videos', str(self.movie_id), self.resolution)
        
        os.makedirs(self.output_folder, exist_ok=True)        
        self.sample_video = os.path.join(settings.BASE_DIR,'videoflix_app', 'tests', 'assets', 'small.mp4')
        assert os.path.exists(self.sample_video), "small.mp4 no found in tests/assets"
        
        generate_hls(
            video_path=self.sample_video,
            output_folder=self.output_folder,
            resolution=self.resolution        )        
        
    
    def tearDown(self):       
        """ Deletes the test media root directory after each test is executed. """
                
        if os.path.exists(self.test_media_root):            
            shutil.rmtree(self.test_media_root)  
        
    def _get_url(self, filename='index.m3u8', movie_id=None):
        """ Returns the URL for a given HLS manifest or segment.
        Args:
            filename: The filename of the HLS manifest or segment.
            movie_id: The ID of the movie for the HLS manifest or segment.
        Returns:
            The URL for the requested HLS manifest or segment. """
            
        movie_id = movie_id or self.movie_id
        if filename == 'index.m3u8':
            return f'/api/video/{movie_id}/{self.resolution}/{filename}'
        else:
            return f'/api/video/{movie_id}/{self.resolution}/{filename}/'


    def test_manifest_served_successfully(self):
        """ Tests that the HLS manifest is served successfully when requested via GET. """
        
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.apple.mpegurl')
        content_bytes = b''.join(response.streaming_content)
        content_str = content_bytes.decode()
        self.assertIn('#EXTM3U', content_str)      

    def test_manifest_not_found(self):
        """ Tests that the HLS manifest is not found when a non-existent movie ID is provided.
        A 404 Not Found status code should be returned in this case. """
        
        response = self.client.get(self._get_url(movie_id=999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manifest_unauthenticated(self):
        """ Tests that an unauthenticated request to the HLS manifest returns a 401 Unauthorized status code. """
        
        self.client.cookies.clear()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_segment_served_successfully(self):
        """ Tests that an HLS segment is served successfully when requested via GET.
        - Asserts that the response status code is 200 OK.
        - Asserts that the response Content-Type is video/MP2T.
        - Asserts that the response content is not empty.       """
        
        segment_filename = 'segment_000.ts'
        response = self.client.get(self._get_url(segment_filename))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'video/MP2T')

        content_bytes = b''.join(response.streaming_content)
        self.assertGreater(len(content_bytes), 0)


    def test_segment_not_found(self):
        """ Tests that a non-existent HLS segment is not found when requested via GET.
        A 404 Not Found status code should be returned in this case. """
        
        response = self.client.get(self._get_url('segment_999.ts'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_segment_unauthenticated(self):
        """ Tests that an unauthenticated request to the HLS segment returns a 401 Unauthorized status code. """
        
        self.client.cookies.clear()
        response = self.client.get(self._get_url('segment_000.ts'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_all_segments_in_manifest_are_accessible(self):        
        """ Tests that all segments listed in the HLS manifest are accessible.
        - Retrieves the HLS manifest and checks for a 200 OK status.
        - Parses the manifest for segment file names.
        - Iterates through each segment file, sending a GET request to ensure:
            - The response status code is 200 OK.
            - The segment content is not empty.  """

        manifest_response = self.client.get(self._get_url())
        self.assertEqual(manifest_response.status_code, status.HTTP_200_OK)
        content_bytes = b''.join(manifest_response.streaming_content)
        manifest_content = content_bytes.decode()

        segment_files = [
            line for line in manifest_content.splitlines()
            if line.endswith('.ts')
        ]
        for segment in segment_files:
            with self.subTest(segment=segment):
                seg_response = self.client.get(self._get_url(segment))
                self.assertEqual(seg_response.status_code, status.HTTP_200_OK)
                seg_content = b''.join(seg_response.streaming_content)
                self.assertGreater(len(seg_content), 0)    
    