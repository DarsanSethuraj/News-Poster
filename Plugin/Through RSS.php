<?php

# Plugin Name: RSS Feed Test

function rss_feed_test_admin_menu() {
    add_menu_page(
        'RSS Feed Test',
        'RSS Feed Test',
        'manage_options',
        'rss-feed-test',
        'rss_feed_test_page'
    );
}

add_action('admin_menu', 'rss_feed_test_admin_menu');

function rss_feed_test_page() {

    require_once ABSPATH . WPINC . '/feed.php';

    $rss = fetch_feed('https://feeds.bbci.co.uk/news/rss.xml');

    echo '<div class="wrap">';
    echo '<h1>BBC RSS Feed Test</h1>';

    if (is_wp_error($rss)) {
        echo '<p>Failed to fetch RSS feed.</p>';
        echo '</div>';
        return;
    }

    $items = $rss->get_items(0, 5);

    if (empty($items)) {
        echo '<p>No feed items found.</p>';
        echo '</div>';
        return;
    }

    echo '<ul>';

    foreach ($items as $item) {
        echo '<li style="margin-bottom:15px;">';

        echo '<strong>' . esc_html($item->get_title()) . '</strong><br>';

        echo '<a href="' . esc_url($item->get_link()) . '" target="_blank">';
        echo esc_html($item->get_link());
        echo '</a>';

        echo '</li>';
    }

    echo '</ul>';
    echo '</div>';
}
