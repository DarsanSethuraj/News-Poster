<?php

# Plugin Name: Admin Page


function backend_test(string $url){

    # post_exists function is not automatically available, so we manually add it
    require_once ABSPATH . 'wp-admin/includes/post.php';

    # fetches a complicated array containing Status code, Headers, Body, Other metadata etc.
    $response = wp_remote_get("http://127.0.0.1:8000/news?url=".urlencode($url));
    
    if (is_wp_error($response)) {
        return "Backend request failed.";
    }

    # Converts a JSON string into a PHP Array
    # wp_remote_retrieve_body => returns only the title and body of the page from the $response safely
    # true => returns it as associative array instead of an object (you can do it with object too, but standard convention is associative array)
    $data = json_decode(wp_remote_retrieve_body($response),true);

    if (empty($data['title']) || empty($data['content'])) {
        return "Failed to fetch article.";
    }

    if (post_exists($data['title'])) {
        return "Post already exists.";
    }

    wp_insert_post([
        'post_title'   => $data['title'],
        'post_content' => $data['content'],
        'post_status'  => 'publish',
        'post_author'  => 1,
    ]);

    return "Post created successfully!";


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
        $message = backend_test($url);

        $notice_class = 'notice-success'; # success gives green color (WP style)

        if (
            $message === 'Backend request failed.' ||
            $message === 'Failed to fetch article.' ||
            $message === 'Please enter a valid URL.' ||
            $message === 'Security check failed.'
        ) {
            $notice_class = 'notice-error'; # gives red color to the msg
        }

        echo '<div class="notice ' . $notice_class . ' is-dismissible">'; # is-dismissible => for option to close the msg
        
        # removes formatting (for safer future uses if code changes)
        echo '<p>' . esc_html($message) . '</p>';
        echo '</div>';

        
    }
}



add_action('admin_menu', 'admin_page');
