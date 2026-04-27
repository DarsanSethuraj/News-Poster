<?php

# Plugin Name: Admin Page


function backend_test(string $url){

    # post_exists function is not automatically available, so we manually add it
    require_once ABSPATH . 'wp-admin/includes/post.php';
    # for setting feautured image functions
    require_once ABSPATH . 'wp-admin/includes/media.php';
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/image.php';

    # fetches a complicated array containing Status code, Headers, Body, Other metadata etc.
    $response = wp_remote_get("http://127.0.0.1:8000/news?url=".urlencode($url));
    
    if (is_wp_error($response)) {
        return [
            'message' => 'Backend request failed.',
            'post_url' => null
        ];
    }

    # Converts a JSON string into a PHP Array
    # wp_remote_retrieve_body => returns only the title and body of the page from the $response safely
    # true => returns it as associative array instead of an object (you can do it with object too, but standard convention is associative array)
    $data = json_decode(wp_remote_retrieve_body($response),true);

    if (empty($data['title']) || empty($data['content'])) {
        return [
            'message' => 'Failed to fetch article.',
            'post_url' => null
        ];
    }

    if (post_exists($data['title'])) {
        return [
            'message' => 'Post already exists.',
            'post_url' => null
        ];
    }

    # if post is not created, then it returns a WP Error due to the 'true'
    $post_id = wp_insert_post([
        'post_title'   => $data['title'],
        'post_content' => $data['content'],
        'post_status'  => 'publish',
        'post_author'  => 1,
    ],true);

    if (is_wp_error($post_id)) {
        return [
            'message' => 'Failed to create post.',
            'post_url' => null
        ];
    }

    # for inserting image into the gallery & associating it with the post
    if (!empty($data['image_url'])) {
        $image_id = media_sideload_image(
            $data['image_url'],
            $post_id,
            null,
            'id'
        );
        # sets it as featured image of the post
        if (!is_wp_error($image_id)) {
            set_post_thumbnail($post_id, $image_id);
        }
    }

    return [
        'message' => 'Post created successfully!',
        'post_url' => get_permalink($post_id)
    ];


}

function admin_page(){

    add_menu_page(
        'Backend Testing',
        'Backend Testing',
        'manage_options',
        'backend-testing',
        'backend_page_html'
    );

}

function backend_page_html() {
    ?>
    <div class="wrap">
        <h1>Backend Testing Page</h1>

        <form method="POST">
            <?php
            # creating security token 
            wp_nonce_field('backend_testing_action', 'backend_testing_nonce'); ?> 

            <input
                type="text"
                name="news_url"
                placeholder="Enter article URL"
                style="width:400px;"
            >

            <button type="submit">
                Fetch News
            </button>
        </form>
    </div>
    <?php

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {  # checks if the form was submitted
        
        # 1st condition => checks if security token field is empty
        # 2nd condition => checks if its valid security token
        if (!isset($_POST['backend_testing_nonce']) || !wp_verify_nonce($_POST['backend_testing_nonce'], 'backend_testing_action')) {
            echo "<p>Security check failed.</p>";
            return;
        }
        
        # sanitizes the url & trim for removing whitespaces
        $url = esc_url_raw(trim($_POST['news_url']));  

        if (empty($url)) {
            echo "<p>Please enter a valid URL.</p>";
            return;
        }
        $result = backend_test($url);
        $message = $result['message'];
        $post_url = $result['post_url'];

        $notice_class = 'notice-success'; # success gives green color (WP style)

        if (
            $message === 'Backend request failed.' ||
            $message === 'Failed to fetch article.' ||
            $message === 'Please enter a valid URL.' ||
            $message === 'Security check failed.' ||
            $message === 'Failed to create post.'
        ) {
            $notice_class = 'notice-error'; # gives red color to the msg
        }

        echo '<div class="notice ' . $notice_class . ' is-dismissible">'; # is-dismissible => for option to close the msg
        
        # removes formatting (for safer future uses if code changes)
        echo '<p>' . esc_html($message) . '</p>';
        echo '</div>';
        if ($post_url) {
            echo '<p>';
            echo '<a href="' . esc_url($post_url) . '" target="_blank" class="button button-primary">';
            echo 'Open Created Post';
            echo '</a>';
            echo '</p>';
        }

        
    }
}



add_action('admin_menu', 'admin_page');
